from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from i18nutils.utils import i18nString
from test_app.models import Product

class TestJSONModels(TestCase):
    """
    Test cases for i18nCharField and i18nTextField model functionality.
    """

    def setUp(self):
        """Set up test data."""
        cache.clear()
        translation.activate('en')
        self.test_product_ids = []

    def test_json_field_storage_and_retrieval(self):
        """Basic storage and retrieval test."""
        product = Product.objects.create(
            name=i18nString({'default': 'Desk', 'en': 'Desk', 'it': 'Scrivania'}),
            description=i18nString({'default': 'Wooden desk', 'it': 'Scrivania in legno'})
        )
        self.test_product_ids.append(product.id)
        
        # Fresh from DB
        p = Product.objects.get(pk=product.pk)
        self.assertIsInstance(p.name, i18nString)
        self.assertEqual(p.name.get('it'), 'Scrivania')
        self.assertEqual(p.name.get('en'), 'Desk')
        
    def test_json_model_basic_creation(self):
        """Test basic model creation with multilingual data."""
        product = Product.objects.create(
            name={'en': 'Test Product', 'fr': 'Produit Test'},
            description={'en': 'Test description', 'fr': 'Description test'}
        )
        self.test_product_ids.append(product.id)
        
        # Reload to trigger from_db_value
        product = Product.objects.get(pk=product.pk)

        translation.activate('en')
        self.assertEqual(str(product.name), 'Test Product')
        self.assertEqual(str(product.description), 'Test description')

        translation.activate('fr')
        self.assertEqual(str(product.name), 'Produit Test')
        self.assertEqual(str(product.description), 'Description test')

    def test_json_model_partial_translation(self):
        """Test model with only partial translations."""
        product = Product.objects.create(
            name={'en': 'Partial Product'},
            description={'en': 'English only', 'fr': 'Français seulement'}
        )
        self.test_product_ids.append(product.id)
        
        product = Product.objects.get(pk=product.pk)

        translation.activate('en')
        self.assertEqual(str(product.name), 'Partial Product')
        self.assertEqual(str(product.description), 'English only')

        translation.activate('fr')
        # Should fallback to default/en if 'fr' is missing in name
        self.assertEqual(str(product.name), 'Partial Product')
        self.assertEqual(str(product.description), 'Français seulement')

    def test_json_model_bulk_operations(self):
        """Test bulk create operations."""
        products_data = [
            {
                'name': {'en': f'Product {i}', 'fr': f'Produit {i}'},
                'description': {'en': f'Description {i}', 'fr': f'Description {i}'}
            }
            for i in range(1, 6)
        ]

        products = [Product.objects.create(**data) for data in products_data]
        self.test_product_ids.extend([p.id for p in products])

        translation.activate('fr')
        for i, product in enumerate(products):
            # Refresh from DB to be sure
            p = Product.objects.get(id=product.id)
            self.assertEqual(str(p.name), f'Produit {i+1}')
            self.assertEqual(str(p.description), f'Description {i+1}')

    def test_json_model_queryset_operations(self):
        """Test queryset operations on products."""
        product1 = Product.objects.create(
            name={'en': 'Alpha Product', 'fr': 'Produit Alpha'},
            description={'en': 'First product'}
        )
        product2 = Product.objects.create(
            name={'en': 'Beta Product', 'fr': 'Produit Beta'},
            description={'en': 'Second product'}
        )
        self.test_product_ids.extend([product1.id, product2.id])

        self.assertEqual(Product.objects.filter(id__in=self.test_product_ids).count(), 2)

        retrieved_product = Product.objects.get(id=product1.id)
        translation.activate('fr')
        self.assertEqual(str(retrieved_product.name), 'Produit Alpha')

    def test_json_field_fallback(self):
        product = Product.objects.create(name={'default': 'Phone'})
        p = Product.objects.get(pk=product.pk)
        self.assertEqual(p.name.get('it'), 'Phone')

    def test_json_field_empty_translations(self):
        product = Product.objects.create(name={'default': 'Book', 'it': ''})
        p = Product.objects.get(pk=product.pk)
        self.assertNotIn('it', p.name._translations)
        self.assertEqual(p.name.get('it'), 'Book')

    def test_json_model_advanced_queries(self):
        """Test advanced Django ORM queries on the JSON field."""
        p1 = Product.objects.create(
            name={'en': 'Red Car', 'it': 'Macchina Rossa'},
            description={'en': 'Fast'}
        )
        p2 = Product.objects.create(
            name={'en': 'Blue Car'}, # Missing 'it'
            description={'en': 'Slow'}
        )
        self.test_product_ids.extend([p1.id, p2.id])

        # 1. Search across all languages (__icontains on the field serializes the JSON to string in SQLite/PG)
        qs_red = Product.objects.filter(name__icontains='Macc')
        self.assertEqual(qs_red.count(), 1)
        self.assertEqual(qs_red.first().id, p1.id)

        # 2. Search specific language with __istartswith
        qs_start = Product.objects.filter(name__en__istartswith='Red')
        self.assertEqual(qs_start.count(), 1)
        self.assertEqual(qs_start.first().id, p1.id)

        # 3. Handle empty/missing strings
        # Our get_prep_value removes empty strings, so the key doesn't exist in the DB
        qs_no_it = Product.objects.filter(name__it__isnull=True)
        # Because we have other products from other tests, we only look at these two
        self.assertIn(p2, qs_no_it)
        self.assertNotIn(p1, qs_no_it)

    def tearDown(self):
        """Clean up test data."""
        Product.objects.filter(id__in=self.test_product_ids).delete()
        cache.clear()
        translation.activate('en')
