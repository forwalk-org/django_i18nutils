from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from test_app.models import Product

class I18nFieldTestCase(TestCase):
    """
    Test cases for i18nField functionality including field creation,
    value assignment, retrieval, and language fallback behavior.
    """

    def setUp(self):
        """Set up test data for i18nField tests."""
        # Clear cache and reset language
        cache.clear()
        translation.activate('en')

        self.product = Product.objects.create(
            name={
                'en': 'Laptop',
                'fr': 'Ordinateur portable',
                'es': 'Portátil',
                'de': 'Laptop'
            },
            description={
                'en': 'High-performance laptop.',
                'fr': 'Ordinateur portable haute performance.',
                'es': 'Portátil de alto rendimiento.',
                'it': 'Laptop ad alte prestazioni.'
            }
        )

        # Store product ID for cleanup
        self.test_product_ids = [self.product.id]

    def test_i18nfield_value_retrieval(self):
        """Test retrieval of translations based on active language."""
        translation.activate('en')
        self.assertEqual(self.product.name, 'Laptop')
        self.assertEqual(self.product.description, 'High-performance laptop.')

        translation.activate('fr')
        self.assertEqual(self.product.name, 'Ordinateur portable')
        self.assertEqual(self.product.description, 'Ordinateur portable haute performance.')

        translation.activate('es')
        self.assertEqual(self.product.name, 'Portátil')
        self.assertEqual(self.product.description, 'Portátil de alto rendimiento.')

    def test_i18nfield_default_fallback(self):
        """Test fallback to default language when translation is missing."""
        translation.activate('zh')  # Chinese is not provided
        self.assertEqual(self.product.name, 'Laptop')  # Fallback to default
        self.assertEqual(self.product.description, 'High-performance laptop.')

    def test_i18nfield_partial_translation_fallback(self):
        """Test fallback behavior when only some translations are missing."""
        translation.activate('it')  # Italian has description but no name
        self.assertEqual(self.product.name, 'Laptop')  # Fallback to default for name
        self.assertEqual(self.product.description, 'Laptop ad alte prestazioni.')  # Italian description

    def test_i18nfield_assignment(self):
        """Test assigning new translations to i18nField."""
        # Add Italian translation
        self.product.name = {'it': 'Portatile'}
        self.product.save()

        translation.activate('it')
        self.assertEqual(self.product.name, 'Portatile')

        # Update existing translation
        self.product.name = {'fr': 'Ordinateur Portable Mis à Jour'}
        self.product.save()

        translation.activate('fr')
        self.assertEqual(self.product.name, 'Ordinateur Portable Mis à Jour')

    def test_i18nfield_single_string_assignment(self):
        """Test assigning a single string instead of dictionary."""
        new_product = Product.objects.create(
            name='Simple Product',
            description='Simple description'
        )
        self.test_product_ids.append(new_product.id)

        translation.activate('en')
        self.assertEqual(new_product.name, 'Simple Product')
        self.assertEqual(new_product.description, 'Simple description')

        translation.activate('fr')
        self.assertEqual(new_product.name, 'Simple Product')  # Fallback
        self.assertEqual(new_product.description, 'Simple description')  # Fallback

    def test_i18nfield_empty_values(self):
        """Test behavior with empty and None values."""
        empty_product = Product.objects.create()
        self.test_product_ids.append(empty_product.id)

        translation.activate('en')
        self.assertIsNone(empty_product.name)
        self.assertIsNone(empty_product.description)

    def test_i18nfield_database_storage(self):
        """Test how translations are stored in the database."""
        # Refresh from database
        product_from_db = Product.objects.get(id=self.product.id)

        translation.activate('fr')
        self.assertEqual(product_from_db.name, 'Ordinateur portable')

        translation.activate('de')
        self.assertEqual(product_from_db.name, 'Laptop')

    def tearDown(self):
        """Clean up test data."""
        # Clean up all test products
        if hasattr(self, 'test_product_ids'):
            Product.objects.filter(id__in=self.test_product_ids).delete()

        # Clear cache
        cache.clear()

        # Reset language to default
        translation.activate('en')
