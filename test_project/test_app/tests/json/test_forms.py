from django.test import TestCase
from django import forms
from test_app.models import Product
from test_app.forms import ProductForm
from i18nutils.utils import i18nString
from i18nutils.forms import I18nFormField

class TestProductForms(TestCase):
    def test_product_form_initial_data(self):
        product = Product.objects.create(
            name=i18nString({'default': 'Table', 'it': 'Tavolo'}),
            description=i18nString({'default': 'Large table', 'it': 'Tavolo grande'})
        )
        form = ProductForm(instance=product)
        # i18nCharField is a single field that uses MultiWidget
        self.assertIsInstance(form.initial['name'], i18nString)
        self.assertEqual(form.initial['name']._translations['default'], 'Table')

    def test_product_form_submission(self):
        # Index mapping based on settings + i18nutils:
        # 0: default, 1: en, 2: en-us, 3: it, ...
        data = {
            'name_0': 'Lamp',     # default
            'name_3': 'Lampada',  # it
            'description_0': 'Bright lamp',
            'description_3': 'Lampada luminosa',
        }
        form = ProductForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        product = form.save()
        self.assertEqual(product.name._translations['default'], 'Lamp')
        self.assertEqual(product.name._translations['it'], 'Lampada')

    def test_product_form_validation_max_length(self):
        # i18nCharField(max_length=255)
        long_name = "A" * 256
        data = {
            'name_0': long_name,
            'name_3': 'Short',
        }
        form = ProductForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_form_clean_with_i18nstring_initial(self):
        """Test that form.clean() handles i18nString initial values correctly."""
        # Use ProductForm which has a name field that uses I18nFormField
        form = ProductForm()
        i18n_value = i18nString({'default': 'Test', 'en': 'Test EN', 'it': 'Test IT'})

        # The name field should handle decomposing i18nString correctly
        name_field = form.fields['name']
        clean_value = name_field.clean(i18n_value)
        self.assertIsInstance(clean_value, i18nString)
        self.assertEqual(clean_value.get('default'), 'Test')
        self.assertEqual(clean_value.get('en'), 'Test EN')
        self.assertEqual(clean_value.get('it'), 'Test IT')

    def test_form_field_labels_no_accumulation(self):
        """Test that form field labels don't accumulate multiple times."""
        # Use ProductForm which is a real form with i18n fields
        form = ProductForm()
        name_field = form.fields['name']

        # Check that each sub-field has the correct label (not accumulated)
        labels = [f.label for f in name_field.fields]

        # Each label should only have ONE language suffix, not accumulated
        # e.g., should be " (default)", not " (default) (en)" or " (default) (en) (it)"
        for label in labels:
            if label:  # Skip None labels
                # Count opening parentheses - should be at most 1
                paren_count = label.count('(')
                self.assertLessEqual(paren_count, 1,
                    f"Label '{label}' has accumulated multiple locale suffixes")

    def test_form_field_labels_without_leading_space(self):
        """Test that form field labels don't start with strange ' (locale)' format."""
        # Use ProductForm which is a real form with i18n fields
        form = ProductForm()
        description_field = form.fields['description']

        # Get labels for all sub-fields
        labels = [f.label for f in description_field.fields if f.label]

        # None should start with " (" which would indicate bad formatting
        for label in labels:
            self.assertFalse(label.startswith(' ('),
                f"Label '{label}' has improper format (starts with space and paren)")
