import logging
import functools
from typing import Union, Optional, Dict, Generator, Any, Callable, Tuple, List
from django.conf import settings
from collections import UserString
from django.utils import translation
from django.utils.functional import Promise
from .fallbacks import FallbackStrategy

# Set up logging
logger = logging.getLogger(__name__)


class i18nString(Promise, UserString):
    """
    Custom string class for handling internationalization.

    Extends Promise and UserString to provide deferred evaluation and string-like
    behaviour. Translations are stored internally as a dict keyed by language code.
    The special key ``'default'`` is used as a fallback when no translation exists
    for the active language.

    The ``data`` property is kept for compatibility with :class:`collections.UserString`:
    reading it returns the string for the current active language.
    """

    def __init__(self, seq: Union[str, Dict[str, str]] = '') -> None:
        """
        Initializes an i18nString instance.

        Args:
            seq (str or dict): A plain string or a ``{lang_code: text}`` dict of
                translations. Pass ``None`` to create an empty instance.
        """
        self._translations: Dict[str, str] = {}
        self.data: Union[str, Dict[str, str]] = seq if seq is not None else ''

    # ------------------------------------------------------------------
    # UserString compatibility — ``data`` property
    # ------------------------------------------------------------------

    def __set_data(self, data: Union[str, Dict[str, str]]) -> None:
        if isinstance(data, dict):
            self._translations = data
        else:
            self._translations[translation.get_language()] = str(data)

    def __get_data(self) -> str:
        return self.get(self.get_language()) or ''

    data = property(__get_data, __set_data)

    # ------------------------------------------------------------------
    # Operators
    # ------------------------------------------------------------------

    def __add__(self, other: Union[str, Promise, 'i18nString']) -> 'i18nString':
        """
        Concatenates another string, Promise or i18nString with this one.

        Returns:
            i18nString: A new i18nString with combined translations.
        """
        data = dict()
        if isinstance(other, i18nString):
            for lang in set(self.languages() + other.languages()):
                data[lang] = (self.get(lang) or '') + (other.get(lang) or '')
        elif isinstance(other, Promise):
            for lang in self.languages():
                with translation.override(lang):
                    data[lang] = (self.get(lang) or '') + str(other)
        else:
            for lang in self.languages():
                data[lang] = (self.get(lang) or '') + other
        return self.__class__(data)

    def __radd__(self, other: Union[str, Promise]) -> 'i18nString':
        """
        Right-hand concatenation (for cases like "Prefix " + i18nString).

        Returns:
            i18nString: A new i18nString with combined translations.
        """
        data = dict()
        if isinstance(other, Promise):
            for lang in self.languages():
                with translation.override(lang):
                    data[lang] = str(other) + (self.get(lang) or '')
        else:
            for lang in self.languages():
                data[lang] = other + (self.get(lang) or '')
        return self.__class__(data)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, lang: str, fallback_routing: Optional[list] = None) -> Optional[str]:
        """
        Returns the translation for *lang*, falling back based on settings.I18NSTRING_FALLBACK_ROUTING 
        or the provided fallback_routing overriding argument.

        Args:
            lang (str): BCP-47 language code.
            fallback_routing (list, optional): Overrides settings.I18NSTRING_FALLBACK_ROUTING.

        Returns:
            str: Translated text, or the default translation if none is found.
        """
        # 1. Exact match
        value = self._translations.get(lang)
        if value is not None:
            return value

        # 2. Iterate over routing strategies
        routing = fallback_routing
        if routing is None:
            routing = getattr(settings, 'I18NSTRING_FALLBACK_ROUTING', [
                FallbackStrategy.REGIONAL_VARIANT,
                FallbackStrategy.DEFAULT_VALUE
            ])

        for strategy_item in routing:
            if isinstance(strategy_item, tuple):
                strategy, args = strategy_item
            else:
                strategy = strategy_item
                args = ()

            if strategy == FallbackStrategy.REGIONAL_VARIANT:
                if lang and '-' in lang:
                    base_lang = lang.split('-')[0]
                    value = self._translations.get(base_lang)
            
            elif strategy == FallbackStrategy.DEFAULT_VALUE:
                value = self._translations.get('default')
            
            elif strategy == FallbackStrategy.FIRST_AVAILABLE:
                langs_to_try = list(args)
                if not langs_to_try:
                    # Dynamically get fallback order from settings if no args provided
                    if hasattr(settings, 'LANGUAGE_CODE'):
                        langs_to_try.append(settings.LANGUAGE_CODE)
                    if hasattr(settings, 'LANGUAGES'):
                        langs_to_try.extend([l_code for l_code, _ in settings.LANGUAGES])
                
                # Deduplicate while preserving order
                seen = set()
                langs_to_try = [l for l in langs_to_try if not (l in seen or seen.add(l))]

                for l in langs_to_try:
                    if l in self._translations:
                        value = self._translations[l]
                        break

            elif strategy == FallbackStrategy.STATIC_VALUE:
                from django.utils.translation import gettext_lazy as _
                val = args[0] if args else _('untranslated text')
                with translation.override(lang):
                    value = str(val)

            if value is not None:
                break

        logger.debug("Translation for language '%s': %s", lang, value)
        return value

    def set(self, lang: str, text: str) -> None:
        """
        Stores a translation for *lang*.

        Raises a ValueError if lang='default' but DEFAULT_VALUE strategy is not 
        active in the routing, or if a generic language code doesn't exist in the project.

        Args:
            lang (str): BCP-47 language code, or 'default'.
            text (str): Translated text.
        """
        if lang == 'default':
            routing = getattr(settings, 'I18NSTRING_FALLBACK_ROUTING', [
                FallbackStrategy.REGIONAL_VARIANT,
                FallbackStrategy.DEFAULT_VALUE
            ])
            has_default = any(
                strategy == FallbackStrategy.DEFAULT_VALUE or 
                (isinstance(strategy, tuple) and strategy[0] == FallbackStrategy.DEFAULT_VALUE)
                for strategy in routing
            )
            if not has_default:
                raise ValueError("Cannot set 'default' value because FallbackStrategy.DEFAULT_VALUE is not active in settings.I18NSTRING_FALLBACK_ROUTING.")
        else:
            if not translation.check_for_language(lang):
                raise ValueError(f"Language '{lang}' is not configured in settings.LANGUAGES.")

        self._translations[lang] = text
        logger.debug("Set translation for language '%s': %s", lang, text)

    def get_language(self) -> str:
        """
        Returns the currently active language, delegating to Django's
        :func:`django.utils.translation.get_language`.

        Returns:
            str: Active language code (e.g. ``'en'``).
        """
        return translation.get_language()

    def languages(self) -> List[str]:
        """
        Returns a list of all language codes for which a translation is stored.

        Returns:
            list[str]: Language codes (e.g. ``['default', 'en', 'it']``).
        """
        return list(self._translations.keys())

    def items(self) -> Generator[Tuple[str, str], None, None]:
        """
        Iterates over ``(language_code, text)`` pairs.

        Yields:
            tuple[str, str]: Language code and its translation.
        """
        for item in self._translations.items():
            yield item

    def get_translations(self) -> Dict[str, str]:
        """
        Returns a copy of all stored translations.

        Returns:
            dict: Dictionary mapping language codes to translated strings.
        """
        return dict(self._translations)


def i18nDecorator(formatter: Optional[Callable[[Any], str]] = None) -> Callable[..., i18nString]:
    """
    Decorator that wraps a function so it returns an :class:`i18nString`.

    The decorated function is called once per language in ``settings.LANGUAGES``.
    If all translations are identical the result is collapsed to a single
    ``{'default': value}`` entry.

    Args:
        formatter (callable, optional): Applied to each raw return value before
            storing it as a translation.

    Returns:
        callable: Wrapper that returns an :class:`i18nString`.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
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
    return decorator
