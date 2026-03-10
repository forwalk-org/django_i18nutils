from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from test_app.models import JSONProduct

class JSONCacheTestCase(TestCase):
    """
    Test cases for caching JSONProduct instances.
    """

    def setUp(self):
        cache.clear()
        translation.activate('en')
        self.test_product_ids = []

    def test_json_product_cache(self):
        """Test caching and retrieving a JSONProduct instance."""
        product = JSONProduct.objects.create(
            name={'en': 'Cached Phone', 'fr': 'Téléphone Caché'},
            description={'en': 'Smart phone'}
        )
        self.test_product_ids.append(product.id)
        
        # Reload to get i18nString instances
        p = JSONProduct.objects.get(id=product.id)
        
        cache_key = f'product_{p.id}'
        cache.set(cache_key, p, 300)
        
        cached_p = cache.get(cache_key)
        self.assertIsNotNone(cached_p)
        
        translation.activate('en')
        self.assertEqual(str(cached_p.name), 'Cached Phone')
        
        translation.activate('fr')
        self.assertEqual(str(cached_p.name), 'Téléphone Caché')

    def tearDown(self):
        JSONProduct.objects.filter(id__in=self.test_product_ids).delete()
        cache.clear()
        translation.activate('en')
