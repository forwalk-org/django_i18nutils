from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from test_app.models import Product

class TranslatableQuerySetTestCase(TestCase):
    """
    Test cases for TranslatableQuerySet functionality, specifically the values() override.
    """

    def setUp(self):
        """Set up test data for QuerySet tests."""
        # Clear cache and reset language
        cache.clear()
        translation.activate('en')

        self.product1 = Product.objects.create(
            name={
                'en': 'Laptop',
                'fr': 'Ordinateur portable',
                'it': 'Portatile'
            },
            description={'en': 'A laptop'}
        )
        self.product2 = Product.objects.create(
            name={
                'en': 'Mouse',
                'fr': 'Souris'
            },
            description={'en': 'A mouse'}
        )
        self.test_ids = [self.product1.id, self.product2.id]

    def test_values_translatable_field(self):
        """Test values() with a translatable field returns JSON object."""
        qs = Product.objects.filter(id__in=self.test_ids).order_by('id').values('name')
        results = list(qs)
        
        self.assertEqual(len(results), 2)
        
        # Check first product
        p1_name = results[0]['name']
        self.assertEqual(p1_name.get('en'), 'Laptop')
        self.assertEqual(p1_name.get('fr'), 'Ordinateur portable')
        self.assertEqual(p1_name.get('it'), 'Portatile')
        
        # Check second product
        p2_name = results[1]['name']
        self.assertEqual(p2_name.get('en'), 'Mouse')
        self.assertEqual(p2_name.get('fr'), 'Souris')
        self.assertIsNone(p2_name.get('it'))

    def test_values_mixed_fields(self):
        """Test values() with both translatable and non-translatable fields."""
        qs = Product.objects.filter(id=self.product1.id).values('id', 'name')
        result = qs[0]
        
        self.assertEqual(result['id'], self.product1.id)
        self.assertEqual(result['name'].get('en'), 'Laptop')

    def test_values_specific_language_field(self):
        """Test values() requesting a specific language field directly."""
        qs = Product.objects.filter(id=self.product1.id).values('name_fr')
        result = qs[0]
        
        self.assertEqual(result['name_fr'], 'Ordinateur portable')

    def tearDown(self):
        Product.objects.filter(id__in=self.test_ids).delete()
        cache.clear()
