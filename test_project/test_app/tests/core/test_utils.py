from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from django.utils.translation import gettext as _
from unittest.mock import patch
from i18nutils.utils import i18nString

class I18nStringTestCase(TestCase):
    """
    Test cases for i18nString functionality including initialization,
    string operations, language management, and integration with Django's translation system.
    """

    def setUp(self):
        """Set up test data for i18nString tests."""
        # Clear cache and reset language
        cache.clear()
        translation.activate('en')

        self.greeting = i18nString({
            'en': 'Hello',
            'fr': 'Bonjour',
            'es': 'Hola',
            'de': 'Hallo',
            'it': 'Ciao'
        })
        self.name = i18nString({
            'en': 'John',
            'fr': 'Jean',
            'es': 'Juan',
            'de': 'Johann',
            'it': 'Giovanni'
        })

        # Store test objects for potential cleanup
        self.test_objects = []

    def test_i18nstring_basic_operations(self):
        """Test basic i18nString initialization and string conversion."""
        translation.activate('en')
        self.assertEqual(str(self.greeting), 'Hello')

        translation.activate('fr')
        self.assertEqual(str(self.greeting), 'Bonjour')

        translation.activate('es')
        self.assertEqual(str(self.greeting), 'Hola')

    def test_i18nstring_concatenation(self):
        """Test string concatenation with i18nString instances."""
        translation.activate('en')
        combined = self.greeting + ' ' + self.name
        self.assertEqual(str(combined), 'Hello John')

        translation.activate('fr')
        combined = self.greeting + ' ' + self.name
        self.assertEqual(str(combined), 'Bonjour Jean')

        translation.activate('es')
        combined = self.greeting + ' ' + self.name
        self.assertEqual(str(combined), 'Hola Juan')

    def test_i18nstring_mixed_concatenation(self):
        """Test concatenation between i18nString and regular strings."""
        translation.activate('en')
        mixed = self.greeting + ', welcome!'
        self.assertEqual(str(mixed), 'Hello, welcome!')

        translation.activate('fr')
        mixed = self.greeting + ', bienvenue!'
        self.assertEqual(str(mixed), 'Bonjour, bienvenue!')

    def test_i18nstring_django_trans_integration(self):
        """Test integration with Django's gettext translation system."""
        # Mock Django's gettext function
        with patch('django.utils.translation.gettext') as mock_gettext:
            mock_gettext.return_value = 'Welcome'

            django_trans = _("Welcome")
            combined = django_trans + ' ' + self.name

            translation.activate('en')
            # This test verifies that i18nString can be combined with Django trans
            self.assertIn('John', str(combined))

    def test_i18nstring_multiple_mixed_concatenation(self):
        """Test concatenation of i18nString + Promise (gettext) + string."""
        with patch('django.utils.translation.gettext') as mock_gettext:
            mock_gettext.return_value = 'Welcome'
            django_trans = _("Welcome")
            
            # i18nString + Promise + str
            combined = self.greeting + ' ' + django_trans + ' to the site!'
            
            translation.activate('en')
            self.assertEqual(str(combined), 'Hello Welcome to the site!')

            # Promise + i18nString + str
            combined2 = django_trans + ' ' + self.name + '!'
            self.assertEqual(str(combined2), 'Welcome John!')

    def test_i18nstring_set_trans(self):
        """Test setting new translations for i18nString."""
        self.greeting.set('pt', 'Olá')
        translation.activate('pt')
        self.assertEqual(str(self.greeting), 'Olá')

    def test_i18nstring_missing_translation_fallback(self):
        """Test fallback behavior when translation is missing."""
        incomplete_greeting = i18nString({'en': 'Hello', 'fr': 'Bonjour'})

        translation.activate('zh')  # Chinese not provided
        self.assertEqual(str(incomplete_greeting), 'Hello') 

        # Test with I18NSTRING_FALLBACK_ROUTING=[]
        with self.settings(I18NSTRING_FALLBACK_ROUTING=[]):
            self.assertIsNone(incomplete_greeting.get('zh'))  # No fallback, returns None

    def test_i18nstring_regional_variant_matching(self):
        """Test fallback to base language for regional variants."""
        msg = i18nString({'en': 'Color', 'en-GB': 'Colour', 'it': 'Colore'})
        
        # Exact match
        self.assertEqual(msg.get('en-GB'), 'Colour')
        
        # Variant match (falls back to base 'en')
        self.assertEqual(msg.get('en-US'), 'Color')
        
        # Test with empty routing
        with self.settings(I18NSTRING_FALLBACK_ROUTING=[]):
            self.assertIsNone(msg.get('en-US'))

    def test_i18nstring_set_invalid_language(self):
        """Test that setting an unconfigured language raises ValueError."""
        with self.assertRaises(ValueError):
            self.greeting.set('invalid-lang', 'Test')

    def test_i18nstring_set_default_invalid_routing(self):
        """Test that setting 'default' requires the DEFAULT_VALUE strategy."""
        with self.settings(I18NSTRING_FALLBACK_ROUTING=[]):
            with self.assertRaises(ValueError):
                self.greeting.set('default', 'Test Default')

    def test_i18nstring_first_available_args(self):
        """Test FIRST_AVAILABLE strategy with explicit arguments."""
        from i18nutils.fallbacks import FallbackStrategy
        msg = i18nString({'fr': 'Bonjour', 'de': 'Hallo'})
        
        with self.settings(I18NSTRING_FALLBACK_ROUTING=[FallbackStrategy.FIRST_AVAILABLE('it', 'de')]):
            self.assertEqual(msg.get('es'), 'Hallo')
            
    def test_i18nstring_first_available_noargs(self):
        """Test FIRST_AVAILABLE strategy dynamic fallback using settings."""
        from i18nutils.fallbacks import FallbackStrategy
        msg = i18nString({'fr': 'Bonjour', 'de': 'Hallo'})
        
        with self.settings(
            I18NSTRING_FALLBACK_ROUTING=[FallbackStrategy.FIRST_AVAILABLE],
            LANGUAGE_CODE='it',
            LANGUAGES=[('en', 'English'), ('de', 'German')]
        ):
            self.assertEqual(msg.get('es'), 'Hallo')

    def test_i18nstring_static_value_fallback(self):
        """Test STATIC_VALUE strategy returns default or custom text."""
        from i18nutils.fallbacks import FallbackStrategy
        msg = i18nString({'fr': 'Bonjour'})
        
        with self.settings(I18NSTRING_FALLBACK_ROUTING=[FallbackStrategy.STATIC_VALUE]):
            self.assertEqual(msg.get('es'), 'untranslated text')
            
        with self.settings(I18NSTRING_FALLBACK_ROUTING=[FallbackStrategy.STATIC_VALUE('Custom')]):
            self.assertEqual(msg.get('es'), 'Custom')
            
    def test_i18nstring_get_fallback_override(self):
        """Test get() with a local fallback_routing bypass."""
        from i18nutils.fallbacks import FallbackStrategy
        msg = i18nString({'fr': 'Bonjour'})
        
        # Override the defaults
        self.assertEqual(msg.get('es', fallback_routing=[FallbackStrategy.STATIC_VALUE('Local')]), 'Local')

    def test_i18nstring_langs(self):
        """Test retrieving all available languages."""
        langs = self.greeting.languages()
        expected_langs = {'en', 'fr', 'es', 'de', 'it'}
        self.assertEqual(set(langs), expected_langs)

    def test_i18nstring_items_iteration(self):
        """Test iterating over language-translation pairs."""
        items = list(self.greeting.items())
        self.assertGreater(len(items), 0)

        # Check that all items are tuples with language and translation
        for lang, trans in items:
            self.assertIsInstance(lang, str)
            self.assertIsInstance(trans, str)
            self.assertGreater(len(lang), 0)
            self.assertGreater(len(trans), 0)

    def test_i18nstring_empty_initialization(self):
        """Test i18nString initialization with empty or invalid data."""
        # Test with empty dict
        empty_string = i18nString({})
        self.assertEqual(str(empty_string), '')

        # Test with None
        none_string = i18nString(None)
        self.assertEqual(str(none_string), '')

    def test_i18nstring_single_string_initialization(self):
        """Test i18nString initialization with a single string."""
        simple_string = i18nString('Simple text')

        translation.activate('en')
        self.assertEqual(str(simple_string), 'Simple text')

        translation.activate('fr')
        self.assertEqual(str(simple_string), 'Simple text')

    def test_i18nstring_complex_concatenation(self):
        """Test complex concatenation scenarios."""
        exclamation = i18nString({
            'en': '!',
            'fr': ' !',
            'es': '!',
            'de': '!',
            'it': '!'
        })

        complex_message = self.greeting + ', ' + self.name + exclamation

        translation.activate('en')
        self.assertEqual(str(complex_message), 'Hello, John!')

        translation.activate('fr')
        self.assertEqual(str(complex_message), 'Bonjour, Jean !')

        translation.activate('de')
        self.assertEqual(str(complex_message), 'Hallo, Johann!')

    def tearDown(self):
        """Clean up test data."""
        # Clean up any test objects that were created
        if hasattr(self, 'test_objects'):
            for obj in self.test_objects:
                if hasattr(obj, 'delete'):
                    obj.delete()

        # Clear cache
        cache.clear()

        # Reset language to default
        translation.activate('en')
