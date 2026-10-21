from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from i18nutils.utils import i18nString
from test_app.models import Product

class JSONEdgeCasesTestCase(TestCase):
    """
    Edge case test cases for i18nCharField and i18nTextField.
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
        product = Product.objects.create(name=unicode_data)
        self.test_product_ids.append(product.id)
        
        p = Product.objects.get(id=product.id)
        translation.activate('ru')
        self.assertEqual(str(p.name), 'Привет 🌏 Мир!')

    def test_json_extreme_language_codes(self):
        """Test handling of unusual language codes in JSON."""
        codes = {
            'en-US': 'American',
            'x-custom': 'Custom',
        }
        product = Product.objects.create(name=codes)
        self.test_product_ids.append(product.id)
        
        p = Product.objects.get(id=product.id)
        # i18nString handles extraction
        self.assertEqual(p.name.get('en-US'), 'American')

    def test_json_none_and_empty_input(self):
        """Test None and empty string inputs for JSON fields."""
        p1 = Product.objects.create(name=None)
        p2 = Product.objects.create(name='')
        self.test_product_ids.extend([p1.id, p2.id])
        
        # Fresh from DB
        obj1 = Product.objects.get(id=p1.id)
        self.assertIn(str(obj1.name), ['', 'None'])
        
        obj2 = Product.objects.get(id=p2.id)
        self.assertIn(str(obj2.name), ['', 'None'])

    def tearDown(self):
        Product.objects.filter(id__in=self.test_product_ids).delete()
        cache.clear()
        translation.activate('en')
