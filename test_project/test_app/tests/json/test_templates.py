from django.test import TestCase
from django.utils import translation
from django.template import Template, Context
from test_app.models import JSONProduct

class JSONTemplateTestCase(TestCase):
    """
    Test cases for JSONProduct in Django templates.
    """

    def setUp(self):
        translation.activate('en')
        self.test_product_ids = []

    def test_json_product_in_template(self):
        """Test rendering JSONProduct fields in a template."""
        product = JSONProduct.objects.create(
            name={'en': 'Template Table', 'it': 'Tavolo Template'},
            description={'en': 'A nice table'}
        )
        self.test_product_ids.append(product.id)
        
        # Reload to get i18nString
        p = JSONProduct.objects.get(id=product.id)
        
        template = Template("Product: {{ product.name }}")
        
        translation.activate('en')
        self.assertIn('Template Table', template.render(Context({'product': p})))
        
        translation.activate('it')
        self.assertIn('Tavolo Template', template.render(Context({'product': p})))

    def tearDown(self):
        JSONProduct.objects.filter(id__in=self.test_product_ids).delete()
        translation.activate('en')
