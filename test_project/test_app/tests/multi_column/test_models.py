from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from test_app.models import Product

class I18nTranslatableModelMixinTestCase(TestCase):
    """
    Test cases for TranslatableModelMixin functionality including model creation,
    field handling, and database operations.
    """

    def setUp(self):
        """Set up test data for TranslatableModelMixin tests."""
        # Clear cache and reset language
        cache.clear()
        translation.activate('en')

        # Track created products for cleanup
        self.test_product_ids = []

    def test_translatablemodelmixin_basic_creation(self):
        """Test basic model creation with TranslatableModelMixin."""
        product = Product.objects.create(
            name={'en': 'Test Product', 'fr': 'Produit Test'},
            description={'en': 'Test description', 'fr': 'Description test'}
        )
        self.test_product_ids.append(product.id)

        translation.activate('en')
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.description, 'Test description')

        translation.activate('fr')
        self.assertEqual(product.name, 'Produit Test')
        self.assertEqual(product.description, 'Description test')

    def test_translatablemodelmixin_partial_translation(self):
        """Test model creation with partial translations."""
        product = Product.objects.create(
            name={'en': 'Partial Product'},
            description={'en': 'English only', 'fr': 'Français seulement'}
        )
        self.test_product_ids.append(product.id)

        translation.activate('en')
        self.assertEqual(product.name, 'Partial Product')
        self.assertEqual(product.description, 'English only')

        translation.activate('fr')
        self.assertEqual(product.name, 'Partial Product')  # Fallback
        self.assertEqual(product.description, 'Français seulement')

    def test_translatablemodelmixin_bulk_operations(self):
        """Test bulk operations with translatable models."""
        products_data = [
            {
                'name': {'en': f'Product {i}', 'fr': f'Produit {i}'},
                'description': {'en': f'Description {i}', 'fr': f'Description {i}'}
            }
            for i in range(1, 6)
        ]

        products = [Product.objects.create(**data) for data in products_data]
        self.test_product_ids.extend([p.id for p in products])

        # Test bulk retrieval
        translation.activate('fr')
        for i, product in enumerate(products):
            self.assertEqual(product.name, f'Produit {i+1}')
            self.assertEqual(product.description, f'Description {i+1}')

    def test_translatablemodelmixin_queryset_operations(self):
        """Test queryset operations with translatable fields."""
        # Create test products
        product1 = Product.objects.create(
            name={'en': 'Alpha Product', 'fr': 'Produit Alpha'},
            description={'en': 'First product'}
        )
        product2 = Product.objects.create(
            name={'en': 'Beta Product', 'fr': 'Produit Beta'},
            description={'en': 'Second product'}
        )
        self.test_product_ids.extend([product1.id, product2.id])

        # Test queryset count
        self.assertEqual(Product.objects.filter(id__in=self.test_product_ids).count(), 2)

        # Test individual retrieval
        retrieved_product = Product.objects.get(id=product1.id)
        translation.activate('fr')
        self.assertEqual(retrieved_product.name, 'Produit Alpha')

    def tearDown(self):
        """Clean up test data."""
        # Clean up all test products
        if hasattr(self, 'test_product_ids') and self.test_product_ids:
            Product.objects.filter(id__in=self.test_product_ids).delete()

        # Clear cache
        cache.clear()

        # Reset language to default
        translation.activate('en')
