# django_i18nutils

A lightweight Django package for handling internationalized model fields and strings. Translations are stored in a single JSON column — no schema migrations needed when adding new languages.

> [!NOTE]
> **Design Philosophy**: Intentionally simple and low-maintenance. No heavy translation workflows or external dependencies — just JSON-backed fields and a smart string class that integrates with Django's i18n layer.

> [!CAUTION]
> **🚨 BREAKING CHANGE (Version 1.0.0)**
> We have completely removed the legacy "Multi-Column" translations approach (which required database migrations to add `_en`, `_it` columns for each language) inside Django models. Translation data is now **strictly stored as a single JSON column**.
> This makes development infinitely easier and more scalable, but **it breaks backwards compatibility** with existing projects relying on the previous SQL structure.
>
> If you need the old Multi-Column tracking structure, you can still install the previous generation targeting our last major commit:
>
> ```bash
> pip install git+https://github.com/forwalk-org/django_i18nutils.git@149f0c4
> ```

## Features

- **`i18nCharField`** and **`i18nTextField`** — single-column JSON storage, backed by Django's `JSONField`.
- **`i18nString`** — a lazy string class (inherits `Promise` + `UserString`) that resolves to the active language at render time.
- **`i18nDecorator`** — decorator that wraps a function and returns an `i18nString` evaluated for every language.

## Installation

```bash
pip install git+https://github.com/forwalk-org/django_i18nutils.git
```

Or clone and install locally:

```bash
git clone https://github.com/forwalk-org/django_i18nutils.git
cd django_i18nutils
pip install .
```

---

## Quick Start

### 1. Configure languages in `settings.py`

```python
from i18nutils.fallbacks import FallbackStrategy

LANGUAGES = [
    ('en', 'English'),
    ('it', 'Italian'),
    ('fr', 'French'),
]

USE_I18N = True

# Define precise resolution rules when a translation is missing.
# Removing FallbackStrategy.DEFAULT_VALUE will block users from setting the 'default' key.
I18NSTRING_FALLBACK_ROUTING = [
    FallbackStrategy.REGIONAL_VARIANT,
    FallbackStrategy.DEFAULT_VALUE,
    FallbackStrategy.FIRST_AVAILABLE('en', 'it') # Tries 'en' then 'it'
]
```

### 2. Add translatable fields to your model

```python
# models.py
from django.db import models
from i18nutils.fields import i18nCharField, i18nTextField

class Article(models.Model):
    # Stored as {"en": "Hello", "it": "Ciao"} in a single JSON column
    title = i18nCharField(max_length=200)
    body  = i18nTextField(null=True, blank=True)
```

### 3. Create and access data

```python
from django.utils import translation

article = Article.objects.create(
    title={'en': 'Hello World', 'it': 'Ciao Mondo'},
    body={'en': 'Content here', 'it': 'Contenuto qui'},
)

translation.activate('it')
print(article.title)  # → Ciao Mondo

translation.activate('fr')
print(article.title)  # → Hello World  (falls back to default)
```

### 4. Querying

Because translations are stored inside Django's native `JSONField`, you can leverage Django's powerful JSON lookups.

#### Target a specific language

You can query precise language keys using `__lang`:

```python
# Exact match in English
Article.objects.filter(title__en='Hello World')

# Case-insensitive "startswith" in Italian
Article.objects.filter(title__it__istartswith='ciao')
```

#### Search across ALL languages simultaneously

By applying lookups directly to the field (without specifying a language key), Django will serialize the JSON payload to text and perform the lookup. This effectively searches the keyword in _every_ translated language at once:

```python
# Matches if "hello" is in English, Italian, French, etc.
Article.objects.filter(title__icontains='hello')
```

#### Handle empty or missing translations

The plugin automatically strips empty strings (`""`) and `None` values before saving. This ensures clean databases, but it means you must use `__isnull` to find items without a translation:

```python
# Find articles that haven't been translated to French yet
Article.objects.filter(title__fr__isnull=True)

# Find articles that HAVE a French translation
Article.objects.filter(title__fr__isnull=False)
```

### 5. Database Indexes (PostgreSQL)

If you plan to perform heavy filtering on translatable fields, we recommend adding a `GinIndex`, supported natively by PostgreSQL, to speed up JSON queries.

```python
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from i18nutils.fields import i18nCharField

class Article(models.Model):
    title = i18nCharField(max_length=200)

    class Meta:
        indexes = [
            # Index the whole JSON field (accelerates `__has_key` and global searches)
            GinIndex(fields=['title'], name='title_gin_idx'),

            # Or index a specific frequently-queried language path
            # GinIndex(fields=['title__en'], name='title_en_gin_idx'),
        ]
```

### 6. Forms & Admin Integration

When you use `i18nCharField` or `i18nTextField`, Django automatically uses the standard `I18nWidget` in your forms. This basic widget generates an input field for _each_ language configured in your settings, stacking them vertically.

#### Django Admin Auto-Detection

For the best User Experience in the Django Admin panel, the tool detects when it's being rendered inside the Admin and **automatically replaces the basic widget with `I18nAdminWidget`**.

This advanced widget features a clean dropdown (Select Box) to quickly switch between languages, displaying only the input for the active language.

- It natively inherits your Django Admin theme.
- It leverages a lightweight Vanilla JS script (no jQuery required).
- It fully supports dynamically added inline forms (e.g., `TabularInline`).

_You don't need to specify or configure anything in your `admin.py` — it works out of the box._

---

## `i18nString` Reference

`i18nString` is a lazy string object that stores a `{lang: text}` dictionary and resolves to the active language when converted to `str`. It is fully compatible with Django's `gettext_lazy` / `Promise` system.

### Construction

```python
from i18nutils.utils import i18nString

# From a dict
s = i18nString({'en': 'Hello', 'it': 'Ciao', 'default': 'Hello'})

# From a plain string (stored under the current active language)
s = i18nString('Hello')
```

### API

| Method                               | Description                                                                                  |
| ------------------------------------ | -------------------------------------------------------------------------------------------- |
| `s.get(lang, fallback_routing=None)` | Return the translation for `lang`. Allows `fallback_routing` array override for local calls. |
| `s.set(lang, text)`                  | Store a translation for `lang` (Validates `lang` exists in project)                          |
| `s.get_language()`                   | Return the current active language (`django.utils.translation.get_language()`)               |
| `s.languages()`                      | Return a list of all stored language codes                                                   |
| `s.items()`                          | Iterate over `(lang, text)` pairs                                                            |

### Concatenation

`i18nString` supports `+` with plain strings, other `i18nString` instances, and Django `Promise` objects (like `gettext_lazy`). You can mix and match them freely:

```python
from i18nutils.utils import i18nString
from django.utils.translation import gettext_lazy as _

greeting = i18nString({'en': 'Hello', 'it': 'Ciao'})
name = i18nString({'en': 'John', 'it': 'Giovanni'})
welcome_trans = _('Welcome to the site')

# i18nString + Promise + str
msg1 = greeting + ' ' + welcome_trans + '!'

# Promise + i18nString + str
msg2 = welcome_trans + ' ' + name + '!'

translation.activate('it')
print(msg1)  # → Ciao Benvenuto nel sito!
print(msg2)  # → Benvenuto nel sito Giovanni!
```

### Fallback logic

When `get(lang)` is called, the resolution order is driven by the strategy pattern explicitly defined in your `settings.I18NSTRING_FALLBACK_ROUTING`.
If not set by the user, the core routing behaves as `[FallbackStrategy.REGIONAL_VARIANT, FallbackStrategy.DEFAULT_VALUE]`.

The sequence is evaluated in order until a translation is found:

- **Exact Match**: The requested language `lang` is found immediately.
- **`REGIONAL_VARIANT`**: e.g., if `'en-US'` is not found, tries its base language `'en'`.
- **`DEFAULT_VALUE`**: Returns the special `'default'` key. This string is extremely useful for un-translatable strings (e.g. brand names) that should be shared across all locales. Note: if this strategy is removed from settings, assigning the `'default'` key is blocked globally (raises `ValueError`).
- **`FIRST_AVAILABLE`**: Tries specific languages in sequence. E.g., `FIRST_AVAILABLE('en', 'fr')`. If called without arguments, it dynamically loads `LANGUAGE_CODE` followed by the keys configured in `LANGUAGES`.
- **`STATIC_VALUE`**: Bypasses translations entirely and returns a hardcoded string or Django lazy text. Defaults to returning `_('untranslated text')` evaluated securely using the exact requested layout via `translation.override(lang)`. Custom example: `STATIC_VALUE('Not available')`.

### Dynamic Routing Override

If you need a specific string or view to behave entirely differently, you can bypass your `settings.I18NSTRING_FALLBACK_ROUTING` dynamically by passing a local array on `get()`:

```python
from i18nutils.fallbacks import FallbackStrategy

# This call will ignore regional and default variants and force a strict static value.
fallback = [FallbackStrategy.STATIC_VALUE('Nessun dato')]
val = article.title.get('it', fallback_routing=fallback)
```

If all these routing strategies fail, the string elegantly resolves to an empty text (`""`).

---

## `i18nDecorator` Reference

Wraps a function so it is evaluated once per language in `settings.LANGUAGES`, returning an `i18nString`.

```python
from i18nutils.utils import i18nDecorator

@i18nDecorator(formatter=str.upper)
def status_label():
    from django.utils.translation import gettext as _
    return _('active')

label = status_label()  # i18nString({'en': 'ACTIVE', 'it': 'ATTIVO', ...})
```

If all language values are identical the result is collapsed to `{'default': value}`.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome!

## Contact

Maurizio Melani — [maurizio@forwalk.org](mailto:maurizio@forwalk.org)
