import logging
from typing import Union, Optional, Dict, Generator, Any, Callable, Tuple, List
from django.conf import settings
from collections import UserString
from django.utils import translation
from django.utils.functional import Promise

# Set up logging
logger = logging.getLogger(__name__)



class i18nString(Promise, UserString):
    """
    Custom string class for handling internationalization.
    Extends Promise and UserString to provide a deferred evaluation and string-like behavior.
    """

    DEFAULT_LANGUAGE: Optional[str] = getattr(settings, 'I18NSTRING_DEFAULT_LANGUAGE', None)

    def __init__(self, seq: Union[str, Dict[str, str]] = '') -> None:
        """
        Initializes an i18nString instance.

        Args:
            seq (str or dict): Initial string data or a dictionary of translations.
        """
        self._data: Dict[str, str] = {}
        self.data: Union[str, Dict[str, str]] = seq

    def __add__(self, other: Union[str, Promise, 'i18nString']) -> 'i18nString':
        """
        Adds another string or i18nString or Promise to this i18nString.

        Args:
            other (str or i18nString): The string to add.

        Returns:
            i18nString: The combined string.
        """

        data = dict()
        if isinstance(other, i18nString):
            for lang in set(self.langs() + other.langs()):
                data[lang] = self.trans(lang) + other.trans(lang)
        elif isinstance(other, Promise):
            for lang in self.langs():
                with translation.override(lang):
                    data[lang] = self.trans(lang) + str(other)
        else:
            for lang in self.langs():
                data[lang] = self.trans(lang) + other
        return self.__class__(data)

    def __set_data(self, data: Union[str, Dict[str, str]]) -> None:
        """
        Sets the data for this i18nString.

        Args:
            data (str or dict): The data to set.
        """
        if isinstance(data, dict):
            self._data = data
        else:
            self._data[translation.get_language()] = str(data)

    def __get_data(self) -> str:
        """
        Gets the current translation based on the active language.

        Returns:
            str: The translated string.
        """
        return self.trans(self.lang())

    data = property(__get_data, __set_data)

    def set_trans(self, lang: str, text: str) -> None:
        """
        Sets a translation for a specific language.

        Args:
            lang (str): The language code.
            text (str): The translated text.
        """
        self._data[lang] = text
        logger.debug("Set translation for language '%s': %s", lang, text)

    def trans(self, lang: str) -> str:
        """
        Retrieves the translation for a given language.

        Args:
            lang (str): The language code.

        Returns:
            str: The translated string.
        """
        data = self._data.get(lang, None)
        if data is None and lang and "-" in lang:
            base_lang = lang.split('-')[0]
            data = self._data.get(base_lang, None)
        if data is None:
            data = self.default_trans()
        logger.debug("Translation for language '%s': %s", lang, data)
        return data

    def default_trans(self) -> str:
        """
        Retrieves the default translation.

        Returns:
            str: The default translated string.
        """
        default_key = 'default' if 'default' in self._data else self.DEFAULT_LANGUAGE
        if not default_key:
            return ''
        return self._data.get(default_key, '')

    def lang(self) -> str:
        """
        Gets the current language.

        Returns:
            str: The language code.
        """
        return translation.get_language()

    def langs(self) -> List[str]:
        """
        Retrieves all available languages in this i18nString.

        Returns:
            list: List of language codes.
        """
        return list(self._data.keys())

    def items(self) -> Generator[Tuple[str, str], None, None]:
        """
        Retrieves all language-translations pairs.

        Yields:
            tuple: A tuple containing language code and translation.
        """
        for item in self._data.items():
            yield item

def i18nDecorator(func: Callable[..., Any], formatter: Optional[Callable[[Any], str]] = None) -> Callable[..., i18nString]:
    """
    A decorator to generate an i18nString from a function.

    Args:
        func (function): The function to decorate.
        formatter (function, optional): A function to format the result.

    Returns:
        function: The wrapped function that returns an i18nString.
    """
    def wrapper(*args: Any, **kwargs: Any) -> i18nString:
        data: Dict[str, str] = dict()
        for lang, _ in settings.LANGUAGES:
            with translation.override(lang):
                if formatter:
                    data[lang] = formatter(func(*args, **kwargs))
                else:
                    data[lang] = str(func(*args, **kwargs))
        if len(set(data.values())) == 1:
            data = {'default': list(data.values())[0]}
        return i18nString(data)
    return wrapper
