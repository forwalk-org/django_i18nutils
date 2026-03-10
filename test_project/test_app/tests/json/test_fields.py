from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from test_app.models import JSONProduct
from i18nutils.utils import i18nString

class JSONFieldTestCase(TestCase):
    """
    Test cases for JSONi18nCharField and JSONi18nTextField functionality,
    mirroring multi_column/test_fields.py.
    """

    def setUp(self):
        """Set up test data."""
        cache.clear()
        translation.activate('en')

        self.product = JSONProduct.objects.create(
            name={
                'en': 'Laptop',
                'fr': 'Ordinateur portable',
                'es': 'Portátil',
                'de': 'Laptop'
            },
            description={
                'en': 'High-performance laptop.',
                'fr': 'Ordinateur portable haute performance.',
                'es': 'Portátil de alto rendimiento.',
                'it': 'Laptop ad alte prestazioni.'
            }
        )
        self.test_product_ids = [self.product.id]

    def test_json_field_value_retrieval(self):
        """Test retrieval of translations for JSON fields."""
        # Reload to ensure from_db_value is called
        p = JSONProduct.objects.get(id=self.product.id)
        
        translation.activate('en')
        self.assertEqual(str(p.name), 'Laptop')
        self.assertEqual(str(p.description), 'High-performance laptop.')

        translation.activate('fr')
        self.assertEqual(str(p.name), 'Ordinateur portable')
        self.assertEqual(str(p.description), 'Ordinateur portable haute performance.')

    def test_json_field_default_fallback(self):
        """Test fallback for JSON fields."""
        p = JSONProduct.objects.get(id=self.product.id)
        translation.activate('zh')
        self.assertEqual(str(p.name), 'Laptop')
        self.assertEqual(str(p.description), 'High-performance laptop.')

    def test_json_field_assignment(self):
        """Test assignment to JSON fields."""
        p = self.product
        p.name = {'it': 'Portatile'}
        p.save()

        reloaded = JSONProduct.objects.get(id=p.id)
        translation.activate('it')
        self.assertEqual(str(reloaded.name), 'Portatile')

    def test_json_field_single_string_assignment(self):
        """Test assigning a single string to a JSON field."""
        new_product = JSONProduct.objects.create(
            name='Simple Product',
            description='Simple description'
        )
        self.test_product_ids.append(new_product.id)

        translation.activate('en')
        self.assertEqual(str(new_product.name), 'Simple Product')

        translation.activate('fr')
        self.assertEqual(str(new_product.name), 'Simple Product')

    def test_json_field_empty_values(self):
        """Test empty values in JSON fields."""
        empty = JSONProduct.objects.create()
        self.test_product_ids.append(empty.id)

        reloaded = JSONProduct.objects.get(id=empty.id)
        self.assertEqual(str(reloaded.name), 'None') # i18nString(None) behavior
        self.assertEqual(str(reloaded.description), 'None')

    def tearDown(self):
        """Clean up."""
        JSONProduct.objects.filter(id__in=self.test_product_ids).delete()
        cache.clear()
        translation.activate('en')
