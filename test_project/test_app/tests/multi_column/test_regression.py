from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from django.db import models
from i18nutils.utils import i18nString
from test_app.models import Product

class I18nRegressionTestCase(TestCase):
    """
    Regression test cases for previously identified issues and bug fixes.
    """

    def setUp(self):
        """Set up test data for regression tests."""
        # Clear cache and reset language
        cache.clear()
        translation.activate('en')

        # Track created products and cache keys for cleanup
        self.test_product_ids = []
        self.cache_keys = []

    def test_empty_translation_handling_regression(self):
        """Regression test for empty translation handling."""
        # This test ensures that empty translations don't cause crashes
        problematic_data = {
            'en': 'Valid English',
            'fr': '',  # Empty French translation
            'es': None,  # None Spanish translation
        }

        text = i18nString(problematic_data)

        translation.activate('en')
        self.assertEqual(str(text), 'Valid English')

        translation.activate('fr')
        # Should handle empty string gracefully
        result = str(text)
        self.assertIsInstance(result, str)

        translation.activate('es')
        # Should handle None gracefully
        result = str(text)
        self.assertIsInstance(result, str)

    def test_database_field_update_regression(self):
        """Regression test for database field update issues."""
        product = Product.objects.create(
            name={'en': 'Original Name'},
            description={'en': 'Original Description'}
        )
        self.test_product_ids.append(product.id)

        # Update with new translations
        product.name = {'en': 'Updated Name', 'fr': 'Nom Mis à Jour'}
        product.description = {'en': 'Updated Description', 'fr': 'Description Mise à Jour'}
        product.save()

        # Refresh from database
        product.refresh_from_db()

        translation.activate('en')
        self.assertEqual(product.name, 'Updated Name')
        self.assertEqual(product.description, 'Updated Description')

        translation.activate('fr')
        self.assertEqual(product.name, 'Nom Mis à Jour')
        self.assertEqual(product.description, 'Description Mise à Jour')

    def test_cache_invalidation_regression(self):
        """Regression test for cache invalidation issues."""
        cache_key = 'regression_test_key'
        self.cache_keys.append(cache_key)

        # Store original content
        original_text = i18nString({'en': 'Original', 'fr': 'Original FR'})
        cache.set(cache_key, original_text, 300)

        # Retrieve and verify
        cached_text = cache.get(cache_key)
        translation.activate('en')
        self.assertEqual(str(cached_text), 'Original')

        # Update cache with new content
        updated_text = i18nString({'en': 'Updated', 'fr': 'Updated FR'})
        cache.set(cache_key, updated_text, 300)

        # Verify update took effect
        cached_text = cache.get(cache_key)
        translation.activate('en')
        self.assertEqual(str(cached_text), 'Updated')

    def test_model_inheritance_regression(self):
        """Regression test for model inheritance issues."""
        # Test that TranslatableModelMixin works with inheritance
        class ExtendedProduct(Product):
            extra_field = models.CharField(max_length=100, default='extra')

            class Meta:
                proxy = True

        # This should work without issues
        extended_product = ExtendedProduct.objects.create(
            name={'en': 'Extended Product'},
            description={'en': 'Extended Description'},
            extra_field='test_value'
        )
        self.test_product_ids.append(extended_product.id)

        translation.activate('en')
        self.assertEqual(extended_product.name, 'Extended Product')
        self.assertEqual(extended_product.extra_field, 'test_value')

    def tearDown(self):
        """Clean up test data."""
        # Clean up all test products
        if hasattr(self, 'test_product_ids') and self.test_product_ids:
            Product.objects.filter(id__in=self.test_product_ids).delete()

        # Clear specific cache keys
        for key in self.cache_keys:
            cache.delete(key)

        # Clear all cache to be safe
        cache.clear()

        # Reset language to default
        translation.activate('en')
