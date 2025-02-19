# django_i18nutils

A Django package for handling internationalized fields and strings. This package provides a flexible way to manage multilingual content within Django models.

## Features

- **i18nField** and **TranslatableModelMixin**: Easily manage multilingual fields in Django models.
- **i18nString**: A utility class for handling internationalized strings.
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

### 1. i18nField and TranslatableModelMixin

The `i18nField` class and `TranslatableModelMixin` work together to simplify the management of multilingual fields in your Django models. The `i18nField` automatically creates separate fields for each language, and the `TranslatableModelMixin` ensures that data is handled correctly during model instance creation.

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

# Usage in a view or shell

# Creating a product with translations
product = Product.objects.create(
    name={
        'en': 'Laptop',
        'fr': 'Ordinateur portable',
        'es': 'Portátil'
    },
    description={
        'en': 'A high-performance laptop.',
        'fr': 'Un ordinateur portable haute performance.',
        'es': 'Un portátil de alto rendimiento.'
    }
)

# Accessing the translated fields based on the current language
from django.utils import translation

# Set the current language to French
translation.activate('fr')
print(product.name)  # Outputs: Ordinateur portable
print(product.description)  # Outputs: Un ordinateur portable haute performance.

# Set the current language to Spanish
translation.activate('es')
print(product.name)  # Outputs: Portátil
print(product.description)  # Outputs: Un portátil de alto rendimiento.

# Adding a new translation
product.name = {'it': 'Portatile'}
product.save()

# Accessing the Italian translation
translation.activate('it')
print(product.name)  # Outputs: Portatile

# Defaulting to a fallback language if translation is missing
translation.activate('de')  # German, which is not provided
print(product.name)  # Outputs the default language translation, e.g., 'Laptop'
```

#### Notes

- **Model Definition**: Inherit from `TranslatableModelMixin` and define `i18nField` fields in your model.
- **Meta Class**: Specify `translate_fields` in your model's `Meta` class, listing all fields that are translatable.
- **Instance Creation**: When creating instances, provide a dictionary with language codes as keys and translations as values.
- **Field Access**: Accessing the field directly returns the translation based on the current active language.

### 2. i18nString

The `i18nString` is a utility class for handling strings in multiple languages. It provides an easy way to manage and manipulate internationalized strings in your applications.

#### Example

```python
from i18nutils.utils import i18nString
from django.utils import translation

# Initialize with a single string (default language)
greeting = i18nString("Hello")

# Initialize with a dictionary of translations
greeting = i18nString({
    'en': 'Hello',
    'fr': 'Bonjour',
    'es': 'Hola'
})

# Retrieve translation based on current language
translation.activate('en')
print(greeting)  # Outputs: Hello

translation.activate('fr')
print(greeting)  # Outputs: Bonjour

# Add two i18nString instances
name = i18nString({'en': 'John', 'fr': 'Jean', 'es': 'Juan'})
greeting_with_name = greeting + ' ' + name
print(greeting_with_name)  # Outputs: Bonjour Jean (when language is set to French)

# Set a new translation
greeting.set_trans('it', 'Ciao')
translation.activate('it')
print(greeting)  # Outputs: Ciao

# Get the default translation
print(greeting.default_trans())  # Outputs: Hello (if default language is English)

# Get all available languages in the i18nString
print(greeting.langs())  # Outputs: ['en', 'fr', 'es', 'it']

# Iterate over all language-translation pairs
for lang, trans in greeting.items():
    print(f"{lang}: {trans}")
    # Outputs:
    # en: Hello
    # fr: Bonjour
    # es: Hola
    # it: Ciao
```

#### Notes

- **Initialization**: Can be initialized with a single string or a dictionary of translations.
- **Language Management**: Automatically handles translations based on Django's current active language.
- **Operations**: Supports string concatenation and other string operations.

### 3. i18nDecorator

The `i18nDecorator` is a decorator that generates `i18nString` instances from functions. It allows you to create functions that return localized strings depending on the active language.

#### Example

```python
from i18nutils.utils import i18nDecorator
from django.utils import translation
import datetime

# Example function that generates a greeting based on the current time
@i18nDecorator
def time_based_greeting():
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        return {
            'en': 'Good morning',
            'fr': 'Bonjour',
            'es': 'Buenos días'
        }
    elif 12 <= current_hour < 18:
        return {
            'en': 'Good afternoon',
            'fr': 'Bon après-midi',
            'es': 'Buenas tardes'
        }
    else:
        return {
            'en': 'Good evening',
            'fr': 'Bonsoir',
            'es': 'Buenas noches'
        }

# Usage
translation.activate('fr')
greeting = time_based_greeting()
print(greeting)  # Outputs the greeting in French based on the current time

# Another example with a formatter function
def uppercase_formatter(value):
    return value.upper()

@i18nDecorator(formatter=uppercase_formatter)
def get_status_message():
    return {
        'en': 'All systems operational',
        'fr': 'Tous les systèmes sont opérationnels',
        'es': 'Todos los sistemas operativos'
    }

translation.activate('en')
status_message = get_status_message()
print(status_message)  # Outputs: ALL SYSTEMS OPERATIONAL
```

#### Notes

- **Decorator Usage**: Use `@i18nDecorator` above your function.
- **Function Return Value**: The decorated function should return a value that will be processed into an `i18nString`.
- **Optional Formatter**: You can pass a formatter function to process the output.

## Configuration

To use `i18nField`, `TranslatableModelMixin`, `i18nString`, and `i18nDecorator`, ensure that your Django project is configured for internationalization. In your `settings.py`, you should have:

```python
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'French'),
    ('es', 'Spanish'),
    # Add more languages as needed
]

# Optionally, set a default language for i18nString
I18NSTRING_DEFAULT_LANGUAGE = 'en'

# Set the default language code for your project
LANGUAGE_CODE = 'en'

# Enable internationalization machinery
USE_I18N = True
```

## Logging

The package uses Python's standard `logging` module. To see debug messages in your Django project, you can configure logging as follows in your `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {  # Optional: Add formatters for better log readability
        'verbose': {
            'format': '[{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
                'formatter': 'verbose',  # Use the formatter defined above
            },
        },
    'loggers': {
        'i18nutils': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        # Include other loggers if needed
    },
}
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue on GitHub.

## Contact

For any questions or inquiries, please contact [Maurizio Melani](mailto:maurizio@forwalk.org).
