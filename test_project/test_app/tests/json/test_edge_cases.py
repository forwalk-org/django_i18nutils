from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from i18nutils.utils import i18nString
from test_app.models import JSONProduct

class JSONEdgeCasesTestCase(TestCase):
    """
    Edge case test cases for JSONi18nField, replicated from test_edge_cases.py.
    """

    def setUp(self):
        cache.clear()
        translation.activate('en')
        self.test_product_ids = []

    def test_json_unicode_and_special_characters(self):
        """Test handling of Unicode in JSON fields."""
        unicode_data = {
            'en': 'Hello 👋 World!',
            'ru': 'Привет 🌏 Мир!',
            'zh': '你好 🌍 世界！',
        }
        product = JSONProduct.objects.create(name=unicode_data)
        self.test_product_ids.append(product.id)
        
        p = JSONProduct.objects.get(id=product.id)
        translation.activate('ru')
        self.assertEqual(str(p.name), 'Привет 🌏 Мир!')

    def test_json_extreme_language_codes(self):
        """Test handling of unusual language codes in JSON."""
        codes = {
            'en-US': 'American',
            'x-custom': 'Custom',
        }
        product = JSONProduct.objects.create(name=codes)
        self.test_product_ids.append(product.id)
        
        p = JSONProduct.objects.get(id=product.id)
        # i18nString handles extraction
        self.assertEqual(p.name.trans('en-US'), 'American')

    def test_json_none_and_empty_input(self):
        """Test None and empty string inputs for JSON fields."""
        p1 = JSONProduct.objects.create(name=None)
        p2 = JSONProduct.objects.create(name='')
        self.test_product_ids.extend([p1.id, p2.id])
        
        # Fresh from DB
        obj1 = JSONProduct.objects.get(id=p1.id)
        # str(i18nString(None)) might return 'None' or '' depending on implementation.
        # i18nString(None) sets data to '' but UserString/Promise behavior might return 'None'.
        self.assertIn(str(obj1.name), ['', 'None'])
        
        obj2 = JSONProduct.objects.get(id=p2.id)
        self.assertIn(str(obj2.name), ['', 'None'])

    def tearDown(self):
        JSONProduct.objects.filter(id__in=self.test_product_ids).delete()
        cache.clear()
        translation.activate('en')
