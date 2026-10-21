from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
import json
from test_app.models import Product
from i18nutils.utils import i18nString

class JSONSerializationTestCase(TestCase):
    """
    Test cases for JSON serialization of Product models with i18n fields.
    """

    def setUp(self):
        cache.clear()
        translation.activate('en')
        self.test_product_ids = []

    def test_product_api_serialization(self):
        """Test serializing Product to JSON for API responses."""
        product = Product.objects.create(
            name={'en': 'JSON Laptop', 'fr': 'Ordinateur JSON'},
            description={'en': 'Cool laptop', 'fr': 'Ordinateur cool'}
        )
        self.test_product_ids.append(product.id)

        def serialize(lang):
            translation.activate(lang)
            # Reload to trigger from_db_value/i18nString
            obj = Product.objects.get(id=product.id)
            return {
                'id': obj.id,
                'name': str(obj.name),
                'description': str(obj.description)
            }

        en_json = json.dumps(serialize('en'))
        fr_json = json.dumps(serialize('fr'))

        self.assertIn('JSON Laptop', en_json)
        self.assertIn('Ordinateur JSON', fr_json)

    def tearDown(self):
        Product.objects.filter(id__in=self.test_product_ids).delete()
        cache.clear()
        translation.activate('en')
