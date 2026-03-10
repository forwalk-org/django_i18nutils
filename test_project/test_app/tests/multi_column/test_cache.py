from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
import pickle
from i18nutils.utils import i18nString

class I18nCacheTestCase(TestCase):
    """
    Test cases for i18nString caching functionality and performance optimization.
    """

    def setUp(self):
        """Set up test data for caching tests."""
        # Clear cache and reset language
        cache.clear()
        translation.activate('en')

        self.cached_greeting = i18nString({
            'en': 'Cached Hello',
            'fr': 'Bonjour en Cache',
            'es': 'Hola en Caché'
        })

        # Base cache keys for cleanup
        self.cache_keys = []

    def test_i18nstring_cache_storage(self):
        """Test that i18nString objects can be stored in cache."""
        cache_key = 'test_greeting'
        self.cache_keys.append(cache_key)

        cache.set(cache_key, self.cached_greeting, 300)

        # Retrieve from cache
        cached_object = cache.get(cache_key)
        self.assertIsNotNone(cached_object)

        translation.activate('en')
        self.assertEqual(str(cached_object), 'Cached Hello')

        translation.activate('fr')
        self.assertEqual(str(cached_object), 'Bonjour en Cache')

    def test_i18nstring_cache_with_language_context(self):
        """Test that cached i18nString maintains language awareness."""
        cache_key = 'multilingual_content'
        self.cache_keys.append(cache_key)

        # Store content in cache
        content = {
            'title': self.cached_greeting,
            'subtitle': i18nString({
                'en': 'Subtitle',
                'fr': 'Sous-titre',
                'es': 'Subtítulo'
            })
        }
        cache.set(cache_key, content, 300)

        # Retrieve and test in different languages
        cached_content = cache.get(cache_key)

        translation.activate('en')
        self.assertEqual(str(cached_content['title']), 'Cached Hello')
        self.assertEqual(str(cached_content['subtitle']), 'Subtitle')

        translation.activate('fr')
        self.assertEqual(str(cached_content['title']), 'Bonjour en Cache')
        self.assertEqual(str(cached_content['subtitle']), 'Sous-titre')

    def test_i18nstring_pickle_serialization(self):
        """Test that i18nString can be pickled/unpickled for caching."""
        # Test pickle serialization
        pickled_data = pickle.dumps(self.cached_greeting)
        unpickled_greeting = pickle.loads(pickled_data)

        translation.activate('es')
        self.assertEqual(str(unpickled_greeting), 'Hola en Caché')

    def test_complex_cached_data_structure(self):
        """Test caching complex data structures containing i18nString objects."""
        cache_key = 'complex_data'
        self.cache_keys.append(cache_key)

        complex_data = {
            'products': [
                {
                    'id': 1,
                    'name': i18nString({'en': 'Product 1', 'fr': 'Produit 1'}),
                    'description': i18nString({'en': 'Description 1', 'fr': 'Description 1'})
                },
                {
                    'id': 2,
                    'name': i18nString({'en': 'Product 2', 'fr': 'Produit 2'}),
                    'description': i18nString({'en': 'Description 2', 'fr': 'Description 2'})
                }
            ],
            'metadata': {
                'title': i18nString({'en': 'Product Catalog', 'fr': 'Catalogue de Produits'})
            }
        }

        cache.set(cache_key, complex_data, 300)
        cached_data = cache.get(cache_key)

        translation.activate('fr')
        self.assertEqual(str(cached_data['products'][0]['name']), 'Produit 1')
        self.assertEqual(str(cached_data['metadata']['title']), 'Catalogue de Produits')

    def tearDown(self):
        """Clear cache after each test."""
        # Clear specific cache keys
        for key in self.cache_keys:
            cache.delete(key)

        # Clear all cache to be safe
        cache.clear()

        # Reset language to default
        translation.activate('en')
