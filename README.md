# django_i18nutils

A Django package for handling internationalized fields and strings. This package provides two ways to manage multilingual content within Django models: **JSON-based fields** (best for flexibility) and **Multi-column fields** (traditional per-language columns).

> [!NOTE]
> **Design Philosophy**: This project is intentionally kept simple and lightweight. We avoid implementing complex translation workflows or heavy dependencies to ensure the package remains low-maintenance and easy to integrate into any Django project.


## Features

- **JSONi18nCharField** and **JSONi18nTextField**: Dynamic, single-column storage using Django's JSONField.
- **i18nField** and **TranslatableModelMixin**: Traditional multi-column internationalized fields.
- **i18nString**: A utility class for handling internationalized strings with support for concatenation and deferred evaluation (`Promise`).
- **i18nDecorator**: A decorator for generating `i18nString` instances from functions.

## Installation

You can install the package directly from GitHub:

```bash
pip install git+https://github.com/forwalk-org/django_i18nutils.git
```

Alternatively, you can clone the repository and install it locally:

```bash
git clone https://github.com/forwalk-org/django_i18nutils.git
cd django_i18nutils
pip install .
```

## Usage

---

### 1. Method A: JSON-based Translatable Fields (Recommended)

This approach stores all translations in a single JSON column. It's the most flexible as it avoids database migrations when adding new languages.

#### Example

```python
# models.py
from django.db import models
from i18nutils.fields import JSONi18nCharField, JSONi18nTextField

class Article(models.Model):
    # Stored as {"en": "Hello", "it": "Ciao"} in a single 'title' column
    title = JSONi18nCharField(max_length=200)
    body = JSONi18nTextField()

# Usage in a view or shell
article = Article.objects.create(
    title={'en': 'Hello World', 'it': 'Ciao Mondo'},
    body={'en': 'Content here', 'it': 'Contenuto qui'}
)

from django.utils import translation
translation.activate('it')
print(article.title)  # Outputs: Ciao Mondo
```

#### Querying and Search
JSON fields allow structured queries into the language keys:
```python
# Search for a specific language
Article.objects.filter(title__en__icontains='Hello')

# Check if a translation key exists
Article.objects.filter(title__it__isnull=False)
```

---

### 2. Method B: Multi-column Fields (Traditional)

The `i18nField` class and `TranslatableModelMixin` work together to create separate fields for each language (e.g., `name_en`, `name_it`).

#### Example

```python
# models.py
from django.db import models
from i18nutils.fields import i18nField
from i18nutils.models import TranslatableModelMixin

class Product(TranslatableModelMixin, models.Model):
    name = i18nField(models.CharField(max_length=255))
    description = i18nField(models.TextField())

    class Meta:
        translate_fields = ['name', 'description']

# Creating a product
product = Product.objects.create(
    name={'en': 'Laptop', 'fr': 'Ordinateur portable'},
    description={'en': 'High-end', 'fr': 'Haut de gamme'}
)

from django.utils import translation
translation.activate('fr')
print(product.name)  # Outputs: Ordinateur portable
```

#### Querying Translatable Fields
You query the specific language columns directly:
```python
# Standard Query
Product.objects.filter(name_en__icontains='Laptop')

# Accessing all translations via values() (returns a dictionary)
product_data = Product.objects.values('name').first()
print(product_data['name']) # {'en': 'Laptop', 'fr': '...', 'default': '...'}
```

---

### Comparison: JSON vs Multi-column

| Feature | JSON Fields (Method A) | Multi-column (Method B) |
| :--- | :--- | :--- |
| **Storage** | Single JSON column | One column per language |
| **Migrations** | **None** for new languages | Requires migration for each language |
| **Query Syntax** | `field__lang__lookup` | `field_lang__lookup` |
| **Efficiency** | Dynamic and scalable | Fixed and strict schema |

---

### 3. i18nString: The Core Utility

The `i18nString` is a powerful utility for handling multilingual strings. It inherits from `django.utils.functional.Promise` (compatible with `gettext_lazy`) and `UserString`.

#### Features & Methods
- **Initialization**: With a string or a dictionary.
- **Concatenation**: Combine `i18nString` with standard `str` or Django `Promise` objects.
- **Fallbacks**: Intelligent logic for falling back to a default language.

#### Example

```python
from i18nutils.utils import i18nString
from django.utils import translation
from django.utils.translation import gettext_lazy as _

# Initialize
greeting = i18nString({'en': 'Hello', 'fr': 'Bonjour'})

# Concatenation support
suffix = _("!") # Lazy promise
full_msg = greeting + " " + suffix

translation.activate('fr')
print(full_msg)  # Outputs: Bonjour !

# Method: set_trans(lang_code, text)
greeting.set_trans('it', 'Ciao')

# Method: items() / langs()
for lang, text in greeting.items():
    print(f"{lang}: {text}")
```

#### Notes

- **Language Management**: Automatically handles translations based on Django's current active language.
- **Technical Note**: Since it's a `Promise`, it integrates seamlessly with Django's lazy loading/evaluation.

### 4. i18nDecorator

Generates `i18nString` instances from functions by evaluating them for every language.

#### Example

```python
from i18nutils.utils import i18nDecorator

@i18nDecorator(formatter=lambda x: x.upper())
def get_greeting():
    return "welcome" 

greeting = get_greeting()
# greeting is now an i18nString with ALL languages in UPPERCASE
```

---

## Configuration

In your `settings.py`:

```python
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'French'),
    ('es', 'Spanish'),
    ('it', 'Italian'),
]

# Set a default fallback language
I18NSTRING_DEFAULT_LANGUAGE = 'en'

USE_I18N = True
```

## Logging

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'i18nutils': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome!

## Contact

Maurizio Melani [maurizio@forwalk.org](mailto:maurizio@forwalk.org).
