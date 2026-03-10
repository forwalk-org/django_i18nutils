from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from test_app.models import JSONProduct
from i18nutils.utils import i18nString

class TestJSONModels(TestCase):
    """
    Test cases for JSONi18nField functionality, replicating tests from test_models.py
    to ensure parity between multi-column and JSON storage approaches.
    """

    def setUp(self):
        """Set up test data."""
        cache.clear()
        translation.activate('en')
        self.test_product_ids = []

    def test_json_field_storage_and_retrieval(self):
        """Basic storage and retrieval test."""
        product = JSONProduct.objects.create(
            name=i18nString({'default': 'Desk', 'en': 'Desk', 'it': 'Scrivania'}),
            description=i18nString({'default': 'Wooden desk', 'it': 'Scrivania in legno'})
        )
        self.test_product_ids.append(product.id)
        
        # Fresh from DB
        p = JSONProduct.objects.get(pk=product.pk)
        self.assertIsInstance(p.name, i18nString)
        self.assertEqual(p.name.trans('it'), 'Scrivania')
        self.assertEqual(p.name.trans('en'), 'Desk')
        
    def test_json_model_basic_creation(self):
        """Replicated from test_models.py: test_translatablemodelmixin_basic_creation"""
        product = JSONProduct.objects.create(
            name={'en': 'Test Product', 'fr': 'Produit Test'},
            description={'en': 'Test description', 'fr': 'Description test'}
        )
        self.test_product_ids.append(product.id)
        
        # Reload to trigger from_db_value
        product = JSONProduct.objects.get(pk=product.pk)

        translation.activate('en')
        self.assertEqual(str(product.name), 'Test Product')
        self.assertEqual(str(product.description), 'Test description')

        translation.activate('fr')
        self.assertEqual(str(product.name), 'Produit Test')
        self.assertEqual(str(product.description), 'Description test')

    def test_json_model_partial_translation(self):
        """Replicated from test_models.py: test_translatablemodelmixin_partial_translation"""
        product = JSONProduct.objects.create(
            name={'en': 'Partial Product'},
            description={'en': 'English only', 'fr': 'Français seulement'}
        )
        self.test_product_ids.append(product.id)
        
        product = JSONProduct.objects.get(pk=product.pk)

        translation.activate('en')
        self.assertEqual(str(product.name), 'Partial Product')
        self.assertEqual(str(product.description), 'English only')

        translation.activate('fr')
        # Should fallback to default/en if 'fr' is missing in name
        self.assertEqual(str(product.name), 'Partial Product')
        self.assertEqual(str(product.description), 'Français seulement')

    def test_json_model_bulk_operations(self):
        """Replicated from test_models.py: test_translatablemodelmixin_bulk_operations"""
        products_data = [
            {
                'name': {'en': f'Product {i}', 'fr': f'Produit {i}'},
                'description': {'en': f'Description {i}', 'fr': f'Description {i}'}
            }
            for i in range(1, 6)
        ]

        products = [JSONProduct.objects.create(**data) for data in products_data]
        self.test_product_ids.extend([p.id for p in products])

        translation.activate('fr')
        for i, product in enumerate(products):
            # Refresh from DB to be sure
            p = JSONProduct.objects.get(id=product.id)
            self.assertEqual(str(p.name), f'Produit {i+1}')
            self.assertEqual(str(p.description), f'Description {i+1}')

    def test_json_model_queryset_operations(self):
        """Replicated from test_models.py: test_translatablemodelmixin_queryset_operations"""
        product1 = JSONProduct.objects.create(
            name={'en': 'Alpha Product', 'fr': 'Produit Alpha'},
            description={'en': 'First product'}
        )
        product2 = JSONProduct.objects.create(
            name={'en': 'Beta Product', 'fr': 'Produit Beta'},
            description={'en': 'Second product'}
        )
        self.test_product_ids.extend([product1.id, product2.id])

        self.assertEqual(JSONProduct.objects.filter(id__in=self.test_product_ids).count(), 2)

        retrieved_product = JSONProduct.objects.get(id=product1.id)
        translation.activate('fr')
        self.assertEqual(str(retrieved_product.name), 'Produit Alpha')

    def test_json_field_fallback(self):
        product = JSONProduct.objects.create(name={'default': 'Phone'})
        p = JSONProduct.objects.get(pk=product.pk)
        self.assertEqual(p.name.trans('it'), 'Phone')

    def test_json_field_empty_translations(self):
        product = JSONProduct.objects.create(name={'default': 'Book', 'it': ''})
        p = JSONProduct.objects.get(pk=product.pk)
        self.assertNotIn('it', p.name._data)
        self.assertEqual(p.name.trans('it'), 'Book')

    def tearDown(self):
        """Clean up test data."""
        JSONProduct.objects.filter(id__in=self.test_product_ids).delete()
        cache.clear()
        translation.activate('en')
