from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
import json
from i18nutils.utils import i18nString
from test_app.models import Product

class I18nJSONSerializationTestCase(TestCase):
    """
    Test cases for JSON serialization compatibility and API integration.
    """

    def setUp(self):
        """Set up test data for JSON serialization tests."""
        # Clear cache and reset language
        cache.clear()
        translation.activate('en')

        # Track created products for cleanup
        self.test_product_ids = []

    def test_i18nstring_json_serialization(self):
        """Test JSON serialization of i18nString objects."""
        text = i18nString({
            'en': 'Hello World',
            'fr': 'Bonjour Monde',
            'es': 'Hola Mundo'
        })

        # Test serialization in different language contexts
        translation.activate('en')
        data = {'message': str(text)}
        json_str = json.dumps(data)
        self.assertIn('Hello World', json_str)

        translation.activate('fr')
        data = {'message': str(text)}
        json_str = json.dumps(data)
        self.assertIn('Bonjour Monde', json_str)

    def test_complex_structure_json_serialization(self):
        """Test JSON serialization of complex structures with i18nString."""
        product = Product.objects.create(
            name={
                'en': 'JSON Test Product',
                'fr': 'Produit Test JSON'
            },
            description={
                'en': 'A product for testing JSON serialization',
                'fr': 'Un produit pour tester la sérialisation JSON'
            }
        )
        self.test_product_ids.append(product.id)

        def serialize_product(lang):
            translation.activate(lang)
            return {
                'id': product.id,
                'name': str(product.name),
                'description': str(product.description),
                'metadata': {
                    'language': lang,
                    'has_translations': len(product.name.langs() if hasattr(product.name, 'langs') else []) > 1
                }
            }

        en_data = serialize_product('en')
        fr_data = serialize_product('fr')

        # Test JSON serialization
        en_json = json.dumps(en_data)
        fr_json = json.dumps(fr_data)

        # Verify serialized content
        self.assertIn('JSON Test Product', en_json)
        self.assertIn('Produit Test JSON', fr_json)

        # Test deserialization
        en_parsed = json.loads(en_json)
        fr_parsed = json.loads(fr_json)

        self.assertEqual(en_parsed['name'], 'JSON Test Product')
        self.assertEqual(fr_parsed['name'], 'Produit Test JSON')

    def test_api_response_consistency(self):
        """Test API response consistency across different languages."""
        # Create test data
        products = [
            Product.objects.create(
                name={
                    'en': f'API Product {i}',
                    'fr': f'Produit API {i}',
                    'es': f'Producto API {i}'
                },
                description={'en': f'Description for product {i}'}
            )
            for i in range(1, 4)
        ]

        def get_api_response(language):
            translation.activate(language)
            return {
                'status': 'success',
                'data': [
                    {
                        'id': product.id,
                        'name': str(product.name),
                        'description': str(product.description)
                    }
                    for product in products
                ],
                'metadata': {
                    'total': len(products),
                    'language': language
                }
            }

        languages = ['en', 'fr', 'es', 'de']
        responses = {lang: get_api_response(lang) for lang in languages}

        # Test structure consistency
        for lang, response in responses.items():
            self.assertEqual(response['status'], 'success')
            self.assertEqual(response['metadata']['total'], 3)
            self.assertEqual(len(response['data']), 3)

            # All products should have valid names and descriptions
            for product_data in response['data']:
                self.assertIsInstance(product_data['name'], str)
                self.assertIsInstance(product_data['description'], str)
                self.assertGreater(len(product_data['name']), 0)
                self.assertGreater(len(product_data['description']), 0)

        # Test language-specific content
        self.assertIn('API Product 1', responses['en']['data'][0]['name'])
        self.assertIn('Produit API 1', responses['fr']['data'][0]['name'])
        self.assertIn('Producto API 1', responses['es']['data'][0]['name'])
        # German should fallback to English
        self.assertIn('API Product 1', responses['de']['data'][0]['name'])

        # Clean up
        for product in products:
            product.delete()

    def tearDown(self):
        """Clean up test data."""
        # Clean up all test products
        if hasattr(self, 'test_product_ids') and self.test_product_ids:
            Product.objects.filter(id__in=self.test_product_ids).delete()

        # Clear cache
        cache.clear()

        # Reset language to default
        translation.activate('en')
