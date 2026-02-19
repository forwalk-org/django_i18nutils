from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from i18nutils.utils import i18nString

class I18nTemplateIntegrationTestCase(TestCase):
    """
    Test cases for Django template integration and rendering.
    """

    def setUp(self):
        """Set up test data for template integration tests."""
        # Clear cache and reset language
        cache.clear()
        translation.activate('en')

    def test_i18nstring_in_template_context(self):
        """Test i18nString objects in Django template contexts."""
        from django.template import Template, Context

        template_str = "{{ title }} - {{ description }}"
        template = Template(template_str)

        context_data = {
            'title': i18nString({
                'en': 'Product Title',
                'fr': 'Titre du Produit'
            }),
            'description': i18nString({
                'en': 'Product Description',
                'fr': 'Description du Produit'
            })
        }

        # Test English rendering
        translation.activate('en')
        context = Context(context_data)
        result = template.render(context)
        self.assertEqual(result, 'Product Title - Product Description')

        # Test French rendering
        translation.activate('fr')
        context = Context(context_data)
        result = template.render(context)
        self.assertEqual(result, 'Titre du Produit - Description du Produit')

    def test_i18nstring_with_template_filters(self):
        """Test i18nString compatibility with Django template filters."""
        from django.template import Template, Context

        template_str = "{{ title|upper }} | {{ title|length }}"
        template = Template(template_str)

        context_data = {
            'title': i18nString({
                'en': 'Hello World',
                'fr': 'Bonjour Monde'
            })
        }

        translation.activate('en')
        context = Context(context_data)
        result = template.render(context)
        self.assertEqual(result, 'HELLO WORLD | 11')

        translation.activate('fr')
        context = Context(context_data)
        result = template.render(context)
        self.assertEqual(result, 'BONJOUR MONDE | 13')

    def test_mixed_i18n_template_content(self):
        """Test mixing i18nString with Django's built-in i18n template tags."""
        from django.template import Template, Context

        # Template mixing i18nString and Django trans tags
        template_str = """
        {% load i18n %}
        {% trans "Welcome" %}: {{ product_name }}
        {% trans "Description" %}: {{ product_description }}
        """

        template = Template(template_str)

        context_data = {
            'product_name': i18nString({
                'en': 'Amazing Product',
                'fr': 'Produit Incroyable'
            }),
            'product_description': i18nString({
                'en': 'This is an amazing product',
                'fr': 'Ceci est un produit incroyable'
            })
        }

        # Test that both work together
        translation.activate('en')
        context = Context(context_data)
        result = template.render(context)
        self.assertIn('Amazing Product', result)

        translation.activate('fr')
        context = Context(context_data)
        result = template.render(context)
        self.assertIn('Produit Incroyable', result)

    def tearDown(self):
        """Clean up test data."""
        # Clear cache
        cache.clear()

        # Reset language to default
        translation.activate('en')
