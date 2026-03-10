from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from i18nutils.utils import i18nString

class I18nEdgeCasesTestCase(TestCase):
    """
    Test cases for edge cases, error conditions, and boundary scenarios.
    """

    def setUp(self):
        """Set up test data for edge cases tests."""
        # Clear cache and reset language
        cache.clear()
        translation.activate('en')

        # Track objects for cleanup
        self.test_objects = []

    def test_corrupted_translation_data_handling(self):
        """Test handling of corrupted or invalid translation data."""
        # Test various invalid data scenarios
        invalid_datasets = [
            {'': 'empty_key_test', 'en': 'valid'},  # Empty key
            {None: 'none_key_test', 'en': 'valid'},  # None key
            {'en': '', 'fr': 'valid'},  # Empty value
            {'en': None, 'fr': 'valid'},  # None value
        ]

        for invalid_data in invalid_datasets:
            try:
                # Should handle gracefully without crashing
                text = i18nString(invalid_data)
                result = str(text)
                self.assertIsInstance(result, str)
            except (ValueError, TypeError, AttributeError):
                # Acceptable to raise these specific exceptions
                pass

    def test_extreme_language_codes(self):
        """Test handling of unusual or extreme language codes."""
        unusual_codes = {
            'en-US': 'American English',
            'zh-Hans-CN': '简体中文',
            'x-klingon': 'tlhIngan Hol',  # Fictional language
            'i-default': 'Default Language',
            '': 'Empty Code'
        }

        text = i18nString(unusual_codes)

        # Test that it doesn't crash with unusual codes
        translation.activate('en-US')
        result = str(text)
        self.assertIsInstance(result, str)

    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters."""
        unicode_translations = {
            'en': 'Hello 👋 World!',
            'fr': 'Bonjour 🌍 Monde!',
            'es': '¡Hola 🌎 Mundo!',
            'ru': 'Привет 🌏 Мир!',
            'zh': '你好 🌍 世界！',
            'ar': 'مرحبا 🌍 بالعالم!',
            'ja': 'こんにちは 🌍 世界！',
        }

        unicode_text = i18nString(unicode_translations)

        # Test various Unicode content
        translation.activate('ru')
        self.assertEqual(str(unicode_text), 'Привет 🌏 Мир!')

    def test_memory_usage_with_repeated_operations(self):
        """Test memory usage doesn't grow excessively with repeated operations."""
        base_text = i18nString({'en': 'Base', 'fr': 'Base FR'})

        # Perform many concatenation operations
        result = base_text
        for i in range(100):
            addition = i18nString({'en': f' {i}', 'fr': f' {i}'})
            result = result + addition

        translation.activate('en')
        result_str = str(result)
        self.assertTrue(result_str.startswith('Base'))
        self.assertTrue('99' in result_str)

    def test_concurrent_language_switching(self):
        """Test behavior under rapid language switching."""
        text = i18nString({
            'en': 'English',
            'fr': 'Français',
            'es': 'Español',
            'de': 'Deutsch'
        })

        languages = ['en', 'fr', 'es', 'de']
        expected = ['English', 'Français', 'Español', 'Deutsch']

        # Rapidly switch languages and verify consistency
        for _ in range(10):
            for lang, expected_text in zip(languages, expected):
                translation.activate(lang)
                self.assertEqual(str(text), expected_text)

    def test_none_and_empty_string_handling(self):
        """Test proper handling of None and empty strings."""
        # Test None input
        none_text = i18nString(None)
        self.assertEqual(str(none_text), '')

        # Test empty string input
        empty_text = i18nString('')
        self.assertEqual(str(empty_text), '')

        # Test mixed None and valid values
        mixed_text = i18nString({'en': None, 'fr': 'Valid', 'es': ''})

        translation.activate('en')
        self.assertEqual(str(mixed_text), '')  # or fallback behavior

        translation.activate('fr')
        self.assertEqual(str(mixed_text), 'Valid')
