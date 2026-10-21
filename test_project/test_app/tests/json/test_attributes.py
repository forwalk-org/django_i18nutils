from django.test import TestCase
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from test_app.models import Product
from i18nutils.utils import i18nString

class JSONAttributesTestCase(TestCase):
    """
    Test cases for standard Django model field attributes (null, blank, index)
    as applied to i18nCharField and i18nTextField.
    """

    def setUp(self):
        translation.activate('en')
        self.test_product_ids = []

    def test_json_field_null_true(self):
        """Test that null=True works as expected."""
        # Create without providing values (should be NULL in DB)
        p = Product.objects.create()
        self.test_product_ids.append(p.id)
        
        reloaded = Product.objects.get(id=p.id)
        self.assertIsNone(reloaded.name)
        self.assertIsNone(reloaded.description)

    def test_json_field_blank_true(self):
        """Test that blank=True works (saving empty values)."""
        # Save empty dict/string
        p = Product.objects.create(name={}, description="")
        self.test_product_ids.append(p.id)
        
        reloaded = Product.objects.get(id=p.id)
        # They should return empty strings when converted to str
        self.assertEqual(str(reloaded.name), '')
        self.assertEqual(str(reloaded.description), '')

    def test_json_field_db_index(self):
        """
        Verify that fields with db_index=True can be queried.
        (The index itself is managed by the DB, but we verify it doesn't break queries).
        """
        name_data = {'en': 'Indexed Product', 'it': 'Prodotto Indicizzato'}
        p = Product.objects.create(name=name_data)
        self.test_product_ids.append(p.id)
        
        results = Product.objects.filter(name=name_data)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results[0].id, p.id)

    def test_json_field_null_assignment(self):
        """Test explicit assignment of None."""
        p = Product.objects.create(name={'en': 'Initial'})
        self.test_product_ids.append(p.id)
        
        p.name = None
        p.save()
        
        reloaded = Product.objects.get(id=p.id)
        self.assertIsNone(reloaded.name)

    def test_radd_with_string(self):
        """Test right-hand concatenation with plain strings (str + i18nString)."""
        s = i18nString({'en': 'World', 'it': 'Mondo'})
        result = 'Hello ' + s

        translation.activate('en')
        self.assertEqual(str(result), 'Hello World')

        translation.activate('it')
        self.assertEqual(str(result), 'Hello Mondo')

    def test_radd_with_promise(self):
        """Test right-hand concatenation with Django's lazy strings."""
        s = i18nString({'en': 'World', 'it': 'Mondo'})
        lazy_prefix = _('Hello')
        result = lazy_prefix + ' ' + s

        translation.activate('en')
        self.assertEqual(str(result), 'Hello World')

        translation.activate('it')
        self.assertEqual(str(result), 'Hello Mondo')

    def tearDown(self):
        Product.objects.filter(id__in=self.test_product_ids).delete()
        translation.activate('en')
