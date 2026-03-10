from django.test import TestCase
from test_app.models import JSONProduct
from test_app.forms import JSONProductForm
from i18nutils.utils import i18nString

class TestJSONProductForms(TestCase):
    def test_json_product_form_initial_data(self):
        product = JSONProduct.objects.create(
            name=i18nString({'default': 'Table', 'it': 'Tavolo'}),
            description=i18nString({'default': 'Large table', 'it': 'Tavolo grande'})
        )
        form = JSONProductForm(instance=product)
        # JSONi18nField is a single field that uses MultiWidget
        self.assertIsInstance(form.initial['name'], i18nString)
        self.assertEqual(form.initial['name']._data['default'], 'Table')

    def test_json_product_form_submission(self):
        # Index mapping based on settings + i18nutils:
        # 0: default, 1: en, 2: en-us, 3: it, ...
        data = {
            'name_0': 'Lamp',     # default
            'name_3': 'Lampada',  # it
            'description_0': 'Bright lamp',
            'description_3': 'Lampada luminosa',
        }
        form = JSONProductForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        product = form.save()
        self.assertEqual(product.name._data['default'], 'Lamp')
        self.assertEqual(product.name._data['it'], 'Lampada')

    def test_json_product_form_validation_max_length(self):
        # JSONi18nCharField(max_length=255)
        long_name = "A" * 256
        data = {
            'name_0': long_name,
            'name_3': 'Short',
        }
        form = JSONProductForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
