from django.test import TestCase
from test_app.models import Product
from test_app.forms import ProductForm

class TestProductForms(TestCase):
    def test_product_form_initial_data(self):
        product = Product.objects.create(
            name={'default': 'Chair', 'it': 'Sedia'},
            description={'default': 'A nice chair', 'it': 'Una bella sedia'}
        )
        form = ProductForm(instance=product)
        # i18nField is not a real field in the DB, it contributes multiple fields
        # So we check for name_default, name_it, etc.
        self.assertEqual(form.initial['name_default'], 'Chair')
        self.assertEqual(form.initial['name_it'], 'Sedia')
