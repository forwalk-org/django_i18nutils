from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from i18nutils.utils import i18nString
from test_app.models import Product

class I18nIntegrationTestCase(TestCase):
    """
    Integration test cases covering real-world scenarios and cross-component functionality.
    """

    def setUp(self):
        """Set up test data for integration tests."""
        # Clear cache and reset language
        cache.clear()
        translation.activate('en')

        # Track created objects for cleanup
        self.test_product_ids = []
        self.cache_keys = []

    def test_multilingual_content_management_system(self):
        """Test a complete multilingual CMS scenario."""
        # Create articles with varying language support
        articles = [
            Product.objects.create(
                name={
                    'en': 'Comprehensive Guide to Web Development',
                    'fr': 'Guide Complet du Développement Web',
                    'es': 'Guía Completa de Desarrollo Web',
                    'de': 'Umfassender Leitfaden zur Webentwicklung'
                },
                description={
                    'en': 'Learn modern web development techniques and best practices',
                    'fr': 'Apprenez les techniques modernes de développement web et les meilleures pratiques',
                    'es': 'Aprende técnicas modernas de desarrollo web y mejores prácticas',
                    'de': 'Lernen Sie moderne Webentwicklungstechniken und bewährte Praktiken'
                }
            ),
            Product.objects.create(
                name={
                    'en': 'Advanced JavaScript Concepts',
                    'fr': 'Concepts JavaScript Avancés'
                },
                description={
                    'en': 'Deep dive into advanced JavaScript programming concepts',
                    'fr': 'Plongée profonde dans les concepts avancés de programmation JavaScript'
                }
            ),
            Product.objects.create(
                name={'en': 'Database Design Patterns'},
                description={'en': 'Essential patterns for effective database design'}
            )
        ]

        # Test content display across different languages
        languages = ['en', 'fr', 'es', 'de', 'it', 'pt']

        for lang in languages:
            translation.activate(lang)

            for i, article in enumerate(articles):
                # All articles should have valid content
                self.assertIsNotNone(article.name)
                self.assertIsNotNone(article.description)
                self.assertGreater(len(str(article.name)), 0)
                self.assertGreater(len(str(article.description)), 0)

                # First article should have translations for supported languages
                if i == 0 and lang in ['en', 'fr', 'es', 'de']:
                    # Verify it's not just falling back to English
                    name_str = str(article.name)
                    if lang == 'fr':
                        self.assertIn('Développement', name_str)
                    elif lang == 'es':
                        self.assertIn('Desarrollo', name_str)
                    elif lang == 'de':
                        self.assertIn('Webentwicklung', name_str)

        # Clean up
        for article in articles:
            article.delete()

    def test_api_serialization_with_mixed_languages(self):
        """Test API response serialization with mixed language support."""
        # Create products with different translation completeness
        products = []
        for i in range(3):
            translations = {'en': f'API Product {i+1}'}
            if i < 2:  # First two have French
                translations['fr'] = f'Produit API {i+1}'
            if i == 0:  # Only first has Spanish
                translations['es'] = f'Producto API {i+1}'

            product = Product.objects.create(
                name=translations,
                description={'en': f'API description for product {i+1}'}
            )
            products.append(product)

        def serialize_products_for_api(language_code):
            """Simulate API serialization."""
            translation.activate(language_code)
            return [
                {
                    'id': product.id,
                    'name': str(product.name),
                    'description': str(product.description),
                }
                for product in products
            ]

        # Test API responses in different languages
        en_response = serialize_products_for_api('en')
        fr_response = serialize_products_for_api('fr')
        es_response = serialize_products_for_api('es')

        # Verify structure consistency
        for response in [en_response, fr_response, es_response]:
            self.assertEqual(len(response), 3)
            for item in response:
                self.assertIn('name', item)
                self.assertIn('description', item)
                self.assertIsInstance(item['name'], str)
                self.assertIsInstance(item['description'], str)

        # Verify language-specific content
        self.assertEqual(en_response[0]['name'], 'API Product 1')
        self.assertEqual(fr_response[0]['name'], 'Produit API 1')
        self.assertEqual(es_response[0]['name'], 'Producto API 1')

        # Products without Spanish should fall back to English
        self.assertEqual(es_response[1]['name'], 'API Product 2')
        self.assertEqual(es_response[2]['name'], 'API Product 3')

    def test_caching_with_multilingual_content(self):
        """Test caching behavior with multilingual content."""
        # Create cached content structure
        cache_key = 'multilingual_page_content'
        self.cache_keys.append(cache_key)

        products_for_cache = []
        product1 = Product.objects.create(
            name={
                'en': 'Featured Product 1',
                'fr': 'Produit Vedette 1',
                'es': 'Producto Destacado 1'
            },
            description={'en': 'Amazing product description'}
        )
        product2 = Product.objects.create(
            name={
                'en': 'Featured Product 2',
                'fr': 'Produit Vedette 2'
            },
            description={'en': 'Another great product'}
        )
        products_for_cache = [product1, product2]
        self.test_product_ids.extend([p.id for p in products_for_cache])

        page_content = {
            'header': {
                'title': i18nString({
                    'en': 'Welcome to Our Platform',
                    'fr': 'Bienvenue sur Notre Plateforme',
                    'es': 'Bienvenido a Nuestra Plataforma'
                }),
                'subtitle': i18nString({
                    'en': 'Your journey starts here',
                    'fr': 'Votre voyage commence ici',
                    'es': 'Tu viaje comienza aquí'
                })
            },
            'products': products_for_cache
        }

        # Cache the content
        cache.set(cache_key, page_content, 300)

        # Retrieve and test in different languages
        def get_localized_page_content(lang):
            translation.activate(lang)
            cached_content = cache.get(cache_key)
            return {
                'header_title': str(cached_content['header']['title']),
                'header_subtitle': str(cached_content['header']['subtitle']),
                'product_names': [str(product.name) for product in cached_content['products']]
            }

        en_content = get_localized_page_content('en')
        fr_content = get_localized_page_content('fr')
        es_content = get_localized_page_content('es')

        # Verify English content
        self.assertEqual(en_content['header_title'], 'Welcome to Our Platform')
        self.assertEqual(en_content['product_names'], ['Featured Product 1', 'Featured Product 2'])

        # Verify French content
        self.assertEqual(fr_content['header_title'], 'Bienvenue sur Notre Plateforme')
        self.assertEqual(fr_content['product_names'], ['Produit Vedette 1', 'Produit Vedette 2'])

        # Verify Spanish content (with fallbacks)
        self.assertEqual(es_content['header_title'], 'Bienvenido a Nuestra Plataforma')
        self.assertEqual(es_content['product_names'], ['Producto Destacado 1', 'Featured Product 2'])

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
