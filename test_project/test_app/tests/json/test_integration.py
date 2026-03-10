from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from i18nutils.utils import i18nString
from test_app.models import JSONProduct

class JSONIntegrationTestCase(TestCase):
    """
    Integration test cases for JSONi18nField, replicated from test_integration.py.
    """

    def setUp(self):
        cache.clear()
        translation.activate('en')
        self.test_product_ids = []

    def test_json_multilingual_cms_scenario(self):
        """Test a complete multilingual CMS scenario with JSON storage."""
        articles = [
            JSONProduct.objects.create(
                name={
                    'en': 'Comprehensive Guide to Web Development',
                    'fr': 'Guide Complet du Développement Web',
                    'es': 'Guía Completa de Desarrollo Web',
                    'de': 'Umfassender Leitfaden zur Webentwicklung'
                },
                description={
                    'en': 'Learn modern web development techniques and best practices',
                    'fr': 'Apprenez les techniques modernes de développement web et les meilleures praticques',
                    'es': 'Aprende técnicas modernas de desarrollo web y mejores prácticas',
                    'de': 'Lernen Sie moderne Webentwicklungstechniken und bewährte Praktiken'
                }
            ),
            JSONProduct.objects.create(
                name={
                    'en': 'Advanced JavaScript Concepts',
                    'fr': 'Concepts JavaScript Avancés'
                },
                description={
                    'en': 'Deep dive into advanced JavaScript programming concepts',
                    'fr': 'Plongée profonde dans les concepts avancés de programmation JavaScript'
                }
            )
        ]
        self.test_product_ids.extend([a.id for a in articles])

        languages = ['en', 'fr', 'es', 'de', 'it']

        for lang in languages:
            translation.activate(lang)
            for i, article in enumerate(articles):
                # Reload from DB to ensure i18nString conversion
                a = JSONProduct.objects.get(id=article.id)
                self.assertIsNotNone(a.name)
                self.assertGreater(len(str(a.name)), 0)

                if i == 0 and lang in ['en', 'fr', 'es', 'de']:
                    name_str = str(a.name)
                    if lang == 'fr':
                        self.assertIn('Développement', name_str)
                    elif lang == 'es':
                        self.assertIn('Desarrollo', name_str)

    def test_json_api_serialization(self):
        """Test JSON field serialization for API-like responses."""
        products = []
        for i in range(3):
            translations = {'en': f'API Product {i+1}'}
            if i < 2:
                translations['fr'] = f'Produit API {i+1}'
            
            product = JSONProduct.objects.create(
                name=translations,
                description={'en': f'API description {i+1}'}
            )
            products.append(product)
        self.test_product_ids.extend([p.id for p in products])

        def serialize(lang):
            translation.activate(lang)
            data = []
            for p in products:
                # Reloading is key for JSON fields
                obj = JSONProduct.objects.get(id=p.id)
                data.append({
                    'name': str(obj.name),
                    'description': str(obj.description)
                })
            return data

        fr_response = serialize('fr')
        self.assertEqual(fr_response[0]['name'], 'Produit API 1')
        self.assertEqual(fr_response[1]['name'], 'Produit API 2')
        # Fallback to English
        self.assertEqual(fr_response[2]['name'], 'API Product 3')

    def test_json_caching(self):
        """Test caching behavior with JSON-based translatable models."""
        cache_key = 'json_cached_product'
        product = JSONProduct.objects.create(
            name={'en': 'Cached', 'fr': 'Caché'},
            description={'en': 'Desc'}
        )
        self.test_product_ids.append(product.id)
        
        # We must store the reloaded object or the i18nString in cache
        p_to_cache = JSONProduct.objects.get(id=product.id)
        cache.set(cache_key, p_to_cache, 300)

        translation.activate('fr')
        cached_p = cache.get(cache_key)
        self.assertEqual(str(cached_p.name), 'Caché')

    def tearDown(self):
        JSONProduct.objects.filter(id__in=self.test_product_ids).delete()
        cache.clear()
        translation.activate('en')
