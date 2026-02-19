import logging
from typing import Union, Optional, Dict, Generator, Any, Callable, Tuple
from django.conf import settings
from django.db.models.fields import Field, CharField, TextField, SlugField
from .utils import i18nString

# Set up logging
logger = logging.getLogger(__name__)

# Get languages from settings
LANGUAGES = ['default'] + [x[0] for x in getattr(settings, 'LANGUAGES', [])]

def to_attr_name(name: str, lang: str) -> str:
    """
    Generates an attribute name based on the field name and language.

    Args:
        name (str): The base name of the attribute.
        lang (str): The language code.

    Returns:
        str: The generated attribute name.
    """
    return "%s_%s" % (name, lang.replace('-', '_'))

def to_translate_field(name: str, value: Union[Dict[str, str], i18nString, str, None]):
    translate_fields = {}
    if isinstance(value, (dict, i18nString)):
        for lang, v in value.items():
            if lang not in LANGUAGES:
                raise ValueError('Language %s is not supported' % lang)
            attr = to_attr_name(name, lang)
            translate_fields[attr] = v
            logger.debug("Set attribute '%s' to '%s' for language '%s'", attr, v, lang)
    elif isinstance(value, str):
        attr = to_attr_name(name, 'default')
        translate_fields[attr] = value
        logger.debug("Set default attribute '%s' to '%s'", attr, value)
    elif value is None:
        for lang in LANGUAGES:
            attr = to_attr_name(name, lang)
            translate_fields[attr] = None
    else:
        raise ValueError('Type %s is not supported' % type(value))
    return translate_fields

class i18nField:
    """
    A custom field class for handling internationalized fields in Django models.
    """

    def __init__(self, field: Field) -> None:
        """
        Initializes an i18nField instance.

        Args:
            field (Field): The Django field to wrap.
        """
        if not isinstance(field, (CharField, TextField, SlugField)):
            raise ValueError('Field Type %s is not supported' % type(field))
        self._field: Field = field
        self.editable: bool = False
        self.creation_counter: int = Field.creation_counter
        Field.creation_counter += len(LANGUAGES)
        logger.debug("Initialized i18nField with field: %s", field)

    def contribute_to_class(self, cls: Any, name: str, private_only: bool = False) -> None:
        """
        Contributes this field to the given model class.

        Args:
            cls (type): The model class to contribute to.
            name (str): The name of the field.
            private_only (bool, optional): Whether to mark the field as private.
        """
        self._name: str = name
        setattr(cls, name, self)

        # Register the base field name with translate_fields in Meta
        add_translate_field = getattr(cls, "add_translate_field", None)
        if callable(add_translate_field):
            add_translate_field(name)

        _, _, args, kwargs = self._field.deconstruct()

        for idx, lang in enumerate(LANGUAGES):
            kwargs.update({
                'verbose_name': "%s (%s)" % (self._field.verbose_name or name, lang),
                'db_column': None
            })
            f = self._field.__class__(*args, **kwargs)
            f.creation_counter = self.creation_counter + idx
            f.contribute_to_class(cls, to_attr_name(name, lang), private_only)
            logger.debug("Contributed field for language '%s': %s", lang, f)

    def __get__(self, obj: Any, objtype: Optional[type] = None) -> Union['i18nField', i18nString]:
        """
        Retrieves the value of this field from the model instance.

        Args:
            obj (models.Model): The model instance.
            objtype (type, optional): The type of the model.

        Returns:
            i18nString: The internationalized string.
        """
        if obj is None:
            return self
        data: Dict[str, str] = dict()
        for lang in LANGUAGES:
            attr = to_attr_name(self._name, lang)
            value = getattr(obj, attr)
            if value:
                data[lang] = value
        if not data:
            return None
        logger.debug("Retrieved i18nString data: %s", data)
        return i18nString(data)

    def __set__(self, obj: Any, value: Union[Dict[str, str], i18nString, str, None]) -> None:
        """
        Sets the value of this field on the model instance.

        Args:
            obj (models.Model): The model instance.
            value (dict, i18nString, str, or None): The value to set.
        """
        translate_fields = to_translate_field(self._name, value)
        for filed_name, v in translate_fields.items():
            setattr(obj, filed_name, v)
