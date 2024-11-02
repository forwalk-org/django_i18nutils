from typing import Dict, Union
from django.test import TestCase
from django.db import models
from .models import TestModel  # Adjust import to match your project's structure
from .utils import i18nString
from .fields import i18nField, to_attr_name

class i18nFieldTestCase(TestCase):

    def setUp(self) -> None:
        """
        Set up the test environment.
        """
        self.model: TestModel = TestModel.objects.create(
            title={"default": "Default Title", "en": "English Title", "fr": "Titre Français"}
        )

    def test_to_attr_name(self) -> None:
        """
        Test the `to_attr_name` utility function.
        """
        attr_name: str = to_attr_name("title", "en")
        self.assertEqual(attr_name, "title_en")

        attr_name = to_attr_name("title", "fr")
        self.assertEqual(attr_name, "title_fr")

    def test_i18nString_initialization(self) -> None:
        """
        Test the initialization of the i18nString class.
        """
        string: i18nString = i18nString({"default": "Hello", "en": "Hello", "fr": "Bonjour"})
        self.assertIsInstance(string, i18nString)
        self.assertEqual(string.trans('en'), "Hello")
        self.assertEqual(string.trans('fr'), "Bonjour")

    def test_i18nString_addition(self) -> None:
        """
        Test the addition of i18nString instances.
        """
        string1: i18nString = i18nString({"default": "Hello", "en": "Hello", "fr": "Bonjour"})
        string2: i18nString = i18nString({"default": " World", "en": " World", "fr": " Monde"})

        result: i18nString = string1 + string2
        self.assertEqual(result.trans('en'), "Hello World")
        self.assertEqual(result.trans('fr'), "Bonjour Monde")

    def test_i18nField_initialization(self) -> None:
        """
        Test the initialization of the i18nField.
        """
        field: i18nField = i18nField(models.CharField(max_length=255))
        self.assertIsInstance(field._field, models.CharField)
        self.assertFalse(field.editable)

    def test_i18nField_data_retrieval(self) -> None:
        """
        Test the retrieval of data from the i18nField.
        """
        title: i18nString = self.model.title
        self.assertIsInstance(title, i18nString)
        self.assertEqual(title.trans('default'), "Default Title")
        self.assertEqual(title.trans('en'), "English Title")
        self.assertEqual(title.trans('fr'), "Titre Français")

    def test_i18nField_data_setting(self) -> None:
        """
        Test setting data on the i18nField.
        """
        new_title: Dict[str, str] = {"default": "New Default Title", "en": "New English Title"}
        self.model.title = new_title
        self.model.save()

        self.model.refresh_from_db()
        title: i18nString = self.model.title

        self.assertEqual(title.trans('default'), "New Default Title")
        self.assertEqual(title.trans('en'), "New English Title")
        self.assertEqual(title.trans('fr'), "Titre Français")  # Should remain unchanged

    def test_i18nField_invalid_language(self) -> None:
        """
        Test setting data with an invalid language code.
        """
        with self.assertRaises(ValueError):
            self.model.title = {"es": "Título en Español"}  # 'es' is not a supported language

    def test_i18nField_invalid_type(self) -> None:
        """
        Test setting an invalid type to the i18nField.
        """
        with self.assertRaises(ValueError):
            self.model.title = 123  # Invalid type

    def test_default_value(self) -> None:
        """
        Test setting a default value on the i18nField.
        """
        self.model.title = "New Default Title Only"
        self.model.save()

        self.model.refresh_from_db()
        title: i18nString = self.model.title

        self.assertEqual(title.trans('default'), "New Default Title Only")
        self.assertNotIn('en', title.langs())
        self.assertNotIn('fr', title.langs())

