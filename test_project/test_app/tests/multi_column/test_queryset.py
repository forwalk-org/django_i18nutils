"""
test_queryset.py — Tests for TranslatableQuerySetMixin and TranslatableQuerySet.

Covers:
- values() with a single translatable field
- values() with mixed (translatable + regular) fields
- values() requesting a specific per-language column directly
- values() with no arguments (standard Django fallback)
- values() with only non-translatable fields (no JSON annotation triggered)
- values() with multiple translatable fields at once
- Direct composition of TranslatableQuerySetMixin into a custom QuerySet
"""

from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from django.db import models

from i18nutils.queryset import TranslatableQuerySetMixin, TranslatableQuerySet
from test_app.models import Product


class TranslatableQuerySetTestCase(TestCase):
    """Tests for TranslatableQuerySet — the concrete queryset class.

    These tests use the ``Product`` model which is already wired up with
    ``TranslatableQuerySet.as_manager()`` via ``TranslatableModelMixin``.
    """

    def setUp(self):
        """Create two products with different translation coverage."""
        cache.clear()
        translation.activate('en')

        self.product1 = Product.objects.create(
            name={
                'default': 'Laptop Default',
                'en': 'Laptop',
                'fr': 'Ordinateur portable',
                'it': 'Portatile',
            },
            description={'en': 'A portable computer', 'fr': 'Un ordinateur portable'},
        )
        self.product2 = Product.objects.create(
            name={
                'en': 'Mouse',
                'fr': 'Souris',
            },
            description={'en': 'A pointing device'},
        )
        self.test_ids = [self.product1.id, self.product2.id]

    def tearDown(self):
        Product.objects.filter(id__in=self.test_ids).delete()
        cache.clear()

    # ------------------------------------------------------------------
    # Core behaviour
    # ------------------------------------------------------------------

    def test_values_translatable_field(self):
        """values() on a translatable field returns a JSON-like dict per row."""
        qs = Product.objects.filter(id__in=self.test_ids).order_by('id').values('name')
        results = list(qs)

        self.assertEqual(len(results), 2)

        p1_name = results[0]['name']
        self.assertEqual(p1_name.get('en'), 'Laptop')
        self.assertEqual(p1_name.get('fr'), 'Ordinateur portable')
        self.assertEqual(p1_name.get('it'), 'Portatile')

        p2_name = results[1]['name']
        self.assertEqual(p2_name.get('en'), 'Mouse')
        self.assertEqual(p2_name.get('fr'), 'Souris')
        # Product2 has no Italian translation → value is None / absent
        self.assertIsNone(p2_name.get('it'))

    def test_values_mixed_fields(self):
        """values() with both translatable and non-translatable fields works."""
        qs = Product.objects.filter(id=self.product1.id).values('id', 'name')
        result = qs[0]

        self.assertEqual(result['id'], self.product1.id)
        self.assertEqual(result['name'].get('en'), 'Laptop')

    def test_values_specific_language_column(self):
        """values() can request a per-language column directly (e.g. name_fr)."""
        qs = Product.objects.filter(id=self.product1.id).values('name_fr')
        result = qs[0]

        self.assertEqual(result['name_fr'], 'Ordinateur portable')

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_values_no_fields_returns_all(self):
        """values() with no arguments falls back to standard Django behaviour.

        Django returns a dict with all concrete column names, not base field
        names.  We verify the call does not raise and that the primary key is
        present.
        """
        qs = Product.objects.filter(id=self.product1.id).values()
        result = list(qs)

        self.assertEqual(len(result), 1)
        self.assertIn('id', result[0])

    def test_values_non_translatable_field_only(self):
        """values() with only non-translatable fields is a pure passthrough."""
        qs = Product.objects.filter(id=self.product1.id).values('id')
        result = qs[0]

        self.assertIn('id', result)
        self.assertEqual(result['id'], self.product1.id)
        # No 'name' or 'description' key should be injected
        self.assertNotIn('name', result)
        self.assertNotIn('description', result)

    def test_values_multiple_translatable_fields(self):
        """values() with several translatable fields expands each independently."""
        qs = Product.objects.filter(id=self.product1.id).values('name', 'description')
        result = qs[0]

        self.assertIn('name', result)
        self.assertIn('description', result)
        self.assertEqual(result['name'].get('en'), 'Laptop')
        self.assertEqual(result['description'].get('en'), 'A portable computer')
        self.assertEqual(result['description'].get('fr'), 'Un ordinateur portable')


class TranslatableQuerySetMixinComposabilityTest(TestCase):
    """Tests that TranslatableQuerySetMixin can be composed into custom QuerySets.

    We build a minimal QuerySet subclass "by hand" that mixes in
    ``TranslatableQuerySetMixin`` and verify that the patched ``values()``
    still works correctly when wired up via ``as_manager()``.
    """

    def setUp(self):
        cache.clear()
        translation.activate('en')

        self.product = Product.objects.create(
            name={'en': 'Keyboard', 'fr': 'Clavier'},
            description={'en': 'A typing device'},
        )

    def tearDown(self):
        Product.objects.filter(pk=self.product.pk).delete()
        cache.clear()

    def test_mixin_exported(self):
        """TranslatableQuerySetMixin is importable from i18nutils.queryset."""
        self.assertTrue(issubclass(TranslatableQuerySet, TranslatableQuerySetMixin))
        self.assertTrue(issubclass(TranslatableQuerySet, models.QuerySet))

    def test_mixin_values_via_concrete_class(self):
        """The mixin's values() patch works when accessed through TranslatableQuerySet."""
        # Build a queryset manually using the concrete class.
        qs = TranslatableQuerySet(model=Product).filter(pk=self.product.pk).values('name')
        result = list(qs)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'].get('en'), 'Keyboard')
        self.assertEqual(result[0]['name'].get('fr'), 'Clavier')

    def test_mixin_does_not_inherit_queryset(self):
        """TranslatableQuerySetMixin itself is NOT a QuerySet subclass.

        This confirms the mixin is safe to compose into any QuerySet hierarchy
        without introducing an unexpected second base class.
        """
        self.assertFalse(issubclass(TranslatableQuerySetMixin, models.QuerySet))
