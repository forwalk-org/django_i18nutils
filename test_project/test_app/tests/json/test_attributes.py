from django.test import TestCase
from django.utils import translation
from test_app.models import JSONProduct
from i18nutils.utils import i18nString

class JSONAttributesTestCase(TestCase):
    """
    Test cases for standard Django model field attributes (null, blank, index)
    as applied to JSONi18nCharField and JSONi18nTextField.
    """

    def setUp(self):
        translation.activate('en')
        self.test_product_ids = []

    def test_json_field_null_true(self):
        """Test that null=True works as expected."""
        # Create without providing values (should be NULL in DB)
        p = JSONProduct.objects.create()
        self.test_product_ids.append(p.id)
        
        reloaded = JSONProduct.objects.get(id=p.id)
        self.assertIsNone(reloaded.name)
        self.assertIsNone(reloaded.description)

    def test_json_field_blank_true(self):
        """Test that blank=True works (saving empty values)."""
        # Save empty dict/string
        p = JSONProduct.objects.create(name={}, description="")
        self.test_product_ids.append(p.id)
        
        reloaded = JSONProduct.objects.get(id=p.id)
        # They should return empty strings when converted to str
        self.assertEqual(str(reloaded.name), '')
        self.assertEqual(str(reloaded.description), '')

    def test_json_field_db_index(self):
        """
        Verify that fields with db_index=True can be queried.
        (The index itself is managed by the DB, but we verify it doesn't break queries).
        """
        name_data = {'en': 'Indexed Product', 'it': 'Prodotto Indicizzato'}
        p = JSONProduct.objects.create(name=name_data)
        self.test_product_ids.append(p.id)
        
        # Test exact match on the JSON blob (Django standard behavior)
        # Note: Querying specific keys inside JSON in Django 
        # usually requires name__en notation which we are investigating in another task, 
        # but here we test standard Field behavior.
        
        results = JSONProduct.objects.filter(name=name_data)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results[0].id, p.id)

    def test_json_field_null_assignment(self):
        """Test explicit assignment of None."""
        p = JSONProduct.objects.create(name={'en': 'Initial'})
        self.test_product_ids.append(p.id)
        
        p.name = None
        p.save()
        
        reloaded = JSONProduct.objects.get(id=p.id)
        self.assertIsNone(reloaded.name)

    def tearDown(self):
        JSONProduct.objects.filter(id__in=self.test_product_ids).delete()
        translation.activate('en')
