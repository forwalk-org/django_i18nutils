from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from test_app.models import Product
import time

class JSONPerformanceTestCase(TestCase):
    """
    Performance tests for Product with JSON i18n fields.
    """

    def setUp(self):
        cache.clear()
        translation.activate('en')
        self.test_product_ids = []

    def test_json_product_retrieval_performance(self):
        """Test performance of retrieving Product with many translations."""
        # Create a product with many translations
        langs = {f'lang_{i}': f'value_{i}' for i in range(50)}
        product = Product.objects.create(name=langs, description=langs)
        self.test_product_ids.append(product.id)

        start_time = time.time()
        for _ in range(100):
            p = Product.objects.get(id=product.id)
            str(p.name) # Trigger conversion
        end_time = time.time() - start_time
        
        # Should be reasonably fast
        self.assertLess(end_time, 1.0)

    def tearDown(self):
        Product.objects.filter(id__in=self.test_product_ids).delete()
        cache.clear()
        translation.activate('en')
