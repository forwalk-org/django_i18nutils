# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**django_i18nutils** is a lightweight Django package for handling internationalized (i18n) model fields and strings. Version 2.0.0 is a **breaking change** that removed the legacy "Multi-Column" approach (which required database migrations for `_en`, `_it` columns). Translation data is now **strictly stored as a single JSON column** using Django's `JSONField`.

Key design philosophy: Intentionally simple and low-maintenance. No heavy translation workflows or external dependencies—just JSON-backed fields and a smart string class that integrates with Django's i18n layer.

## Directory Structure

```
i18nutils/               # Main package
├── __init__.py          # Version info
├── fields.py            # i18nCharField, i18nTextField (JSON-backed model fields)
├── forms.py             # Form widgets (I18nWidget, I18nAdminWidget) and form fields
├── utils.py             # i18nString class (lazy string that resolves per-language)
└── fallbacks.py         # FallbackStrategy enum (resolution strategies for missing translations)

test_project/            # Minimal Django test project
├── manage.py
├── test_app/            # Test application with models, forms, admin, views
└── test_project/        # Django settings, URLs, WSGI

script/
├── test-local.sh        # Run tox inside Docker container (divio/multi-python)
```

## Architecture & Core Components

### 1. **i18nString** (`utils.py`)
A custom string class that extends `Promise` (Django's lazy evaluation) and `UserString`. Stores translations as a dict keyed by language code.

- **Key Features:**
  - Lazy evaluation: resolves to the active language when converted to `str`
  - Compatible with Django's `gettext_lazy` and Promise objects
  - Supports concatenation with `+` operator across i18nString, Promise, and plain strings
  - Smart fallback routing via `FallbackStrategy`

- **Main Methods:**
  - `get(lang, fallback_routing=None)`: Returns translation for a language with fallback logic
  - `set(lang, text)`: Store a translation for a language
  - `languages()`: List all stored language codes
  - `items()`: Iterate over (lang, text) pairs

### 2. **i18n Fields** (`fields.py`)
JSON-backed Django model fields that store all translations in a single column.

- **Classes:**
  - `i18nFieldMixin`: Shared logic for both field types
  - `i18nCharField` / `i18nTextField`: Extend Django's `JSONField` with i18n behavior

- **Key Behavior:**
  - `to_python()`: Converts DB values to `i18nString` instances
  - `get_prep_value()`: Strips empty strings and `None` before saving (keeps DB clean)
  - `formfield()`: Detects admin context and provides appropriate widgets automatically

### 3. **Form Widgets** (`forms.py`)
Two sets of widgets:

- **Standard Widgets** (`I18nWidget`, `I18nTextInput`, `I18nTextarea`):
  - Generates one input field per language, stacked vertically
  - Used in regular forms and non-admin views

- **Admin Widgets** (`I18nAdminWidget`, `I18nAdminTextInput`, `I18nAdminTextarea`):
  - Provides a dropdown to switch languages
  - Displays only the active language's input
  - Vanilla JS (no jQuery), supports dynamic inlines
  - Automatically detected and used in Django Admin

### 4. **Fallback Strategies** (`fallbacks.py`)
Determines how missing translations are resolved. Configured in `settings.I18NSTRING_FALLBACK_ROUTING`.

Available strategies:
- `REGIONAL_VARIANT`: Tries base language (e.g., `'en'` for `'en-US'`)
- `DEFAULT_VALUE`: Returns special `'default'` key
- `FIRST_AVAILABLE('en', 'it')`: Tries specific languages in order
- `STATIC_VALUE('text')`: Hardcoded fallback

## Development Commands

### Setup
```bash
# Install in development mode
pip install -e .

# Install test dependencies
pip install pytest pytest-django coverage tox
```

### Testing

**Run tests locally (current Python/Django):**
```bash
# Using Django test runner
python test_project/manage.py test test_app

# Using pytest (if installed)
pytest test_project/test_app/tests/

# Run a specific test module
python test_project/manage.py test test_app.tests.json.test_fields

# Run a single test class/method
python test_project/manage.py test test_app.tests.json.test_fields.TestI18nCharField.test_basic_access
```

**Run full test matrix (all Python/Django combinations):**
```bash
# Using tox (covers all Python 3.8-3.13 and Django 3.2-6.0)
tox

# Using Docker (no need to install multiple Python versions)
script/test-local.sh

# Run specific environment
tox -e py312-django51

# Run with verbose output
tox -v
```

### Linting & Code Quality
Currently no dedicated linting setup in the repo. If needed, consider:
- `black` for code formatting
- `flake8` or `ruff` for linting
- `isort` for import sorting

## Testing Architecture

Tests are located in `test_project/test_app/tests/`:

- `core/` — Core utility tests (fallback logic, string resolution)
- `json/` — Main test suites for JSON fields, forms, models, integration, performance, regression
  - `test_fields.py` — Field behavior, querying, admin detection
  - `test_forms.py` — Form widget rendering, admin widget behavior
  - `test_models.py` — Model field storage and retrieval
  - `test_integration.py` — End-to-end workflows
  - `test_performance.py` — Performance benchmarks
  - `test_regression.py` — Regression tests for known issues

Django settings for tests: `test_project/test_project/settings.py`
- Uses SQLite by default
- Configured with all necessary i18n settings
- Test database is created in-memory

## Key Files to Know

| File | Purpose |
|------|---------|
| `README.md` | Installation, quick start, API reference |
| `setup.py` | Package metadata and dependencies |
| `tox.ini` | Test matrix configuration (Python 3.8-3.13, Django 3.2-6.0) |
| `.github/workflows/ci.yml` | GitHub Actions CI pipeline |
| `test_project/test_app/models.py` | Test models using i18n fields |
| `test_project/test_app/forms.py` | Test forms |
| `test_project/test_app/admin.py` | Test admin registration |

## Important Notes

### Version 2.0.0 Breaking Change
- **Removed:** Multi-Column approach (legacy `_en`, `_it` columns)
- **Now:** All translations stored in a single JSON column
- **Migration Path:** Existing projects using the old approach can pin to commit `149f0c4` or earlier

### Django Admin Integration
The package automatically detects when fields are rendered in the Django Admin and provides `I18nAdminWidget` without requiring any configuration. Regular forms get the basic `I18nWidget` (stacked inputs).

### Empty Value Handling
Empty strings (`""`) and `None` values are automatically stripped during `get_prep_value()`. This keeps the database clean but means you must use `field__lang__isnull=True` to find untranslated items.

### JSONField Querying
Because the package uses Django's native `JSONField`, you get access to powerful JSON lookups:
- `Article.objects.filter(title__en='Hello')` — Exact match in English
- `Article.objects.filter(title__icontains='hello')` — Search across all languages
- `Article.objects.filter(title__fr__isnull=False)` — Has French translation

## Common Patterns

### Adding a New i18n Field
```python
from i18nutils.fields import i18nCharField, i18nTextField

class MyModel(models.Model):
    title = i18nCharField(max_length=200)
    description = i18nTextField(null=True, blank=True)
```

No database migration needed—just a new JSONField column.

### Configuring Fallback Strategy
```python
# settings.py
from i18nutils.fallbacks import FallbackStrategy

I18NSTRING_FALLBACK_ROUTING = [
    FallbackStrategy.REGIONAL_VARIANT,
    FallbackStrategy.DEFAULT_VALUE,
    FallbackStrategy.FIRST_AVAILABLE('en', 'it'),
]
```

### Querying with Indexes
For heavy filtering on translatable fields, add a `GinIndex` (PostgreSQL):
```python
from django.contrib.postgres.indexes import GinIndex

class MyModel(models.Model):
    title = i18nCharField(max_length=200)
    
    class Meta:
        indexes = [GinIndex(fields=['title'], name='title_gin_idx')]
```

## Contributing & PR Guidelines

- Run tests locally before pushing: `python test_project/manage.py test test_app`
- Use tox for comprehensive testing: `tox` or `script/test-local.sh`
- Keep changes focused on a single feature or fix
- Update tests if behavior changes
- Update README.md for user-facing changes
