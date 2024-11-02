
# django_i18nutils

A Django package for handling internationalized fields and strings. This package provides a flexible way to manage multilingual content within Django models.

## Features

- **i18nString**: A custom string class for handling internationalization with support for multiple languages.
- **i18nField**: A Django model field wrapper that allows easy management of multilingual fields.

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

### 1. i18nString

The `i18nString` class allows you to handle strings in multiple languages. You can initialize it with either a single string or a dictionary containing translations.

#### Example

```python
from i18nutils.utils import i18nString

# Initialize with a single string (default language)
greeting = i18nString("Hello")

# Initialize with a dictionary of translations
greeting = i18nString({
    'en': 'Hello',
    'fr': 'Bonjour',
    'es': 'Hola'
})

# Retrieve translation based on current language
print(greeting)  # Outputs "Hello" if the current language is English

# Add two i18nString instances
greeting_with_name = greeting + i18nString({'en': ' John', 'fr': ' Jean'})
print(greeting_with_name)  # Outputs "Hello John" or "Bonjour Jean" based on the language

# Set a new translation
greeting.set_trans('it', 'Ciao')
print(greeting.trans('it'))  # Outputs "Ciao"

# Get the default translation
print(greeting.default_trans())  # Outputs "Hello" (if default language is English)

# Get the current language
print(greeting.lang())  # Outputs the current language code (e.g., "en")

# Get all available languages in the i18nString
print(greeting.langs())  # Outputs ['en', 'fr', 'es', 'it']

# Get all language-translation pairs
for lang, trans in greeting.items():
    print(f"{lang}: {trans}")  # Outputs each language and its corresponding translation
```

### 2. i18nField

The `i18nField` class is a custom Django model field that simplifies the management of multilingual fields. It automatically creates separate fields for each language and handles the logic for retrieving and setting the correct translation.

#### Example

```python
from django.db import models
from i18nutils.fields import i18nField

class Product(models.Model):
    name = i18nField(models.CharField(max_length=255))
    description = i18nField(models.TextField())

# Usage in a view or shell
product = Product.objects.create(
    name={'en': 'Laptop', 'fr': 'Ordinateur portable', 'es': 'Portátil'},
    description={'en': 'A high-performance laptop.', 'fr': 'Un ordinateur portable haute performance.'}
)

# Accessing the translated fields
print(product.name)  # Outputs the name based on the current language
print(product.description.trans('fr'))  # Outputs "Un ordinateur portable haute performance."

# Setting a new translation
product.name = {'en': 'Tablet', 'fr': 'Tablette'}
product.save()

# Accessing the updated translation
print(product.name.trans('en'))  # Outputs "Tablet"
```

## Configuration

To use `i18nString` and `i18nField`, ensure that your Django project is configured for internationalization. In your `settings.py`, you should have:

```python
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'French'),
    ('es', 'Spanish'),
    # Add more languages as needed
]

# Optionally, set a default language for i18nString
I18NSTRING_DEFAULT_LANGUAGE = 'en'
```

## Logging

The package uses Python's standard `logging` module. To see debug messages in your Django project, you can configure logging as follows in your `settings.py`:

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

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue on GitHub.

## Contact

For any questions or inquiries, please contact [Maurizio Melani](mailto:maurizio@forwalk.org).
