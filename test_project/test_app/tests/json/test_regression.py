from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from i18nutils.utils import i18nString
from test_app.models import Product

class JSONRegressionTestCase(TestCase):
    """
    Regression test cases for i18nCharField and i18nTextField.
    """

    def setUp(self):
        cache.clear()
        translation.activate('en')
        self.test_product_ids = []

    def test_json_empty_translation_regression(self):
        """Ensure empty/None translations in JSON don't crash."""
        product = Product.objects.create(
            name={'en': 'Valid', 'fr': '', 'es': None}
        )
        self.test_product_ids.append(product.id)
        
        p = Product.objects.get(id=product.id)
        
        translation.activate('en')
        self.assertEqual(str(p.name), 'Valid')
        
        translation.activate('fr')
        self.assertEqual(str(p.name), 'Valid') # Fallback because '' is stripped by get_prep_value

    def test_json_database_field_update_regression(self):
        """Test updating JSON fields with new translations."""
        product = Product.objects.create(name={'en': 'Original'})
        self.test_product_ids.append(product.id)
        
        product.name = {'en': 'Updated', 'fr': 'Mis à jour'}
        product.save()
        
        p = Product.objects.get(id=product.id)
        translation.activate('fr')
        self.assertEqual(str(p.name), 'Mis à jour')

    def test_json_inheritance_regression(self):
        """Test JSON fields with proxy models (inheritance)."""
        from django.db import models
        class ProxyProduct(Product):
            class Meta:
                proxy = True
        
        p = ProxyProduct.objects.create(name={'en': 'Proxy'})
        self.test_product_ids.append(p.id)
        
        reloaded = ProxyProduct.objects.get(id=p.id)
        self.assertEqual(str(reloaded.name), 'Proxy')

    def tearDown(self):
        Product.objects.filter(id__in=self.test_product_ids).delete()
        cache.clear()
        translation.activate('en')
