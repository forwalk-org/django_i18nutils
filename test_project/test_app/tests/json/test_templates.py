from django.test import TestCase
from django.utils import translation
from django.template import Template, Context
from test_app.models import Product

class JSONTemplateTestCase(TestCase):
    """
    Test cases for Product with i18n fields in Django templates.
    """

    def setUp(self):
        translation.activate('en')
        self.test_product_ids = []

    def test_product_in_template(self):
        """Test rendering Product i18n fields in a template."""
        product = Product.objects.create(
            name={'en': 'Template Table', 'it': 'Tavolo Template'},
            description={'en': 'A nice table'}
        )
        self.test_product_ids.append(product.id)
        
        # Reload to get i18nString
        p = Product.objects.get(id=product.id)
        
        template = Template("Product: {{ product.name }}")
        
        translation.activate('en')
        self.assertIn('Template Table', template.render(Context({'product': p})))
        
        translation.activate('it')
        self.assertIn('Tavolo Template', template.render(Context({'product': p})))

    def tearDown(self):
        Product.objects.filter(id__in=self.test_product_ids).delete()
        translation.activate('en')
