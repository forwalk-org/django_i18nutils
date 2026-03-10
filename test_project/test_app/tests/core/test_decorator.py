from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from i18nutils.utils import i18nDecorator

class I18nDecoratorTestCase(TestCase):
    """
    Test cases for i18nDecorator functionality including function decoration,
    return value processing, and formatter integration.
    """

    def setUp(self):
        """Set up test data for decorator tests."""
        translation.activate('en')

    @staticmethod
    def lazy_trans(data):
        """Utility return str in current language"""
        lang = translation.get_language()
        return data.get(lang, '')

    def test_i18ndecorator_basic_usage(self):
        """Test basic i18nDecorator functionality."""
        @i18nDecorator()
        def get_greeting():
            return self.lazy_trans({
                'en': 'Good morning',
                'fr': 'Bonjour',
                'es': 'Buenos días'
            })

        translation.activate('en')
        greeting = get_greeting()
        self.assertEqual(str(greeting), 'Good morning')

        translation.activate('fr')
        greeting = get_greeting()
        self.assertEqual(str(greeting), 'Bonjour')

    def test_i18ndecorator_with_formatter(self):
        """Test i18nDecorator with custom formatter function."""
        def uppercase_formatter(value):
            return value.upper()

        @i18nDecorator(formatter=uppercase_formatter)
        def get_status():
            return self.lazy_trans({
                'en': 'System operational',
                'fr': 'Système opérationnel',
                'es': 'Sistema operativo'
            })

        translation.activate('en')
        status = get_status()
        self.assertEqual(str(status), 'SYSTEM OPERATIONAL')

        translation.activate('fr')
        status = get_status()
        self.assertEqual(str(status), 'SYSTÈME OPÉRATIONNEL')

    def test_i18ndecorator_dynamic_content(self):
        """Test i18nDecorator with dynamic content generation."""
        import datetime

        @i18nDecorator()
        def time_based_greeting():
            current_hour = datetime.datetime.now().hour
            if current_hour < 12:
                return self.lazy_trans({
                    'en': 'Good morning',
                    'fr': 'Bonjour',
                    'es': 'Buenos días'
                })
            else:
                return self.lazy_trans({
                    'en': 'Good afternoon',
                    'fr': 'Bon après-midi',
                    'es': 'Buenas tardes'
                })

        translation.activate('en')
        greeting = time_based_greeting()
        self.assertIn(str(greeting), ['Good morning', 'Good afternoon'])

    def test_i18ndecorator_with_parameters(self):
        """Test i18nDecorator with parameterized functions."""
        @i18nDecorator()
        def get_welcome_message(name):
            return self.lazy_trans({
                'en': f'Welcome, {name}!',
                'fr': f'Bienvenue, {name}!',
                'es': f'¡Bienvenido, {name}!'
            })

        translation.activate('en')
        message = get_welcome_message('Alice')
        self.assertEqual(str(message), 'Welcome, Alice!')

        translation.activate('fr')
        message = get_welcome_message('Alice')
        self.assertEqual(str(message), 'Bienvenue, Alice!')

    def tearDown(self):
        """Clean up test data."""
        # Clear cache
        cache.clear()

        # Reset language to default
        translation.activate('en')
