from django.test import TestCase
from django.utils import translation
from django.core.cache import cache
from i18nutils.utils import i18nString
import time

class I18nPerformanceTestCase(TestCase):
    """
    Test cases focused on performance benchmarks and optimization verification.
    """

    def setUp(self):
        """Set up test data for performance tests."""
        # Clear cache and reset language
        cache.clear()
        translation.activate('en')

    def test_i18nstring_creation_performance(self):
        """Test performance of i18nString creation with various sizes."""

        # Small dataset
        small_data = {f'lang_{i}': f'text_{i}' for i in range(10)}
        start_time = time.time()
        for _ in range(100):
            i18nString(small_data)
        small_time = time.time() - start_time

        # Large dataset
        large_data = {f'lang_{i}': f'text_{i}' for i in range(100)}
        start_time = time.time()
        for _ in range(100):
            i18nString(large_data)
        large_time = time.time() - start_time

        # Performance should not degrade dramatically
        self.assertLess(large_time, small_time * 20)  # Allow 20x degradation max

    def test_concatenation_performance(self):
        """Test performance of string concatenation operations."""

        base_text = i18nString({'en': 'Base', 'fr': 'Base FR'})
        addon_text = i18nString({'en': ' Addition', 'fr': ' Ajout'})

        start_time = time.time()
        for _ in range(1000):
            result = base_text + addon_text
            str(result)  # Force evaluation
        concat_time = time.time() - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(concat_time, 5.0)  # 5 seconds max

    def test_language_switching_performance(self):
        """Test performance of frequent language switching."""

        text = i18nString({
            'en': 'English text with some content',
            'fr': 'Texte français avec du contenu',
            'es': 'Texto español con contenido',
            'de': 'Deutscher Text mit Inhalt'
        })

        languages = ['en', 'fr', 'es', 'de']

        start_time = time.time()
        for _ in range(1000):
            for lang in languages:
                translation.activate(lang)
                str(text)  # Force string conversion
        switch_time = time.time() - start_time

        # Should handle frequent switching efficiently
        self.assertLess(switch_time, 10.0)  # 10 seconds max

    def tearDown(self):
        """Clean up test data."""
        # Clear cache
        cache.clear()

        # Reset language to default
        translation.activate('en')
