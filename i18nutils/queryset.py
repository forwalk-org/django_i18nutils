"""
queryset.py — Translatable QuerySet utilities for django-i18nutils.

This module provides two public symbols:

* :class:`TranslatableQuerySetMixin`  — a pure mixin that patches ``values()``
  so that any field listed in the model's ``translate_fields`` attribute is
  automatically expanded into a JSON object keyed by language code.  Use this
  mixin when you already have your own ``QuerySet`` subclass and want to add
  i18n support without changing the inheritance chain.

* :class:`TranslatableQuerySet` — a ready-to-use concrete ``QuerySet`` that
  inherits from both ``TranslatableQuerySetMixin`` and ``models.QuerySet``.
  This is what :class:`i18nutils.models.TranslatableModelMixin` wires up by
  default.

Example — using the mixin with a custom QuerySet::

    from django.db import models
    from i18nutils.queryset import TranslatableQuerySetMixin

    class MyQuerySet(TranslatableQuerySetMixin, models.QuerySet):
        def published(self):
            return self.filter(is_published=True)

    class Article(TranslatableModelMixin, models.Model):
        objects = MyQuerySet.as_manager()

Example — using the concrete class directly (same as the default)::

    from i18nutils.queryset import TranslatableQuerySet
    from i18nutils.models import TranslatableModelMixin
    from django.db import models

    class Article(TranslatableModelMixin, models.Model):
        objects = TranslatableQuerySet.as_manager()
"""

import logging
from django.db import models
from django.db.models import F
from django.db.models.functions import JSONObject
from django.conf import settings

logger = logging.getLogger(__name__)


class TranslatableQuerySetMixin:
    """Mixin that patches :meth:`values` to expand translatable fields.

    When ``values()`` is called with one or more field names that appear in the
    model's ``translate_fields`` list, each such field is replaced by a
    ``JSONObject`` annotation that contains every language variant stored in
    the database.  All other fields are forwarded to the standard Django
    ``values()`` unchanged.

    The language list is built at query time from
    ``settings.LANGUAGES`` (prefixed with ``'default'``), which is the same
    convention used by :class:`i18nutils.fields.i18nField` when naming the
    individual database columns (e.g. ``name_default``, ``name_en``,
    ``name_fr``).

    This class is intentionally **not** a ``QuerySet`` subclass so that it can
    be mixed into any existing ``QuerySet`` hierarchy via normal Python MRO.

    Usage::

        class MyQuerySet(TranslatableQuerySetMixin, models.QuerySet):
            ...

    .. note::
        If ``values()`` is called with *no* positional arguments the call is
        forwarded to the parent implementation as-is (standard Django
        behaviour: returns all concrete fields).
    """

    def values(self, *fields, **expressions):
        """Return a ``ValuesQuerySet`` with translatable fields expanded.

        Each field name listed in ``fields`` is checked against the model's
        ``translate_fields`` attribute.  If it matches, the field is replaced
        by a ``JSONObject`` annotation keyed by language code; otherwise it is
        passed through unchanged.

        Args:
            *fields: Optional field names to include in the result dict.
                When empty the call is forwarded to Django's default
                ``values()`` without any transformation.
            **expressions: Named expressions forwarded verbatim to the parent
                ``values()`` call.

        Returns:
            ValuesQuerySet: A queryset whose rows are dicts.  Translatable
            fields are represented as dicts of ``{lang: value}`` instead of
            raw column values.

        Example::

            # Returns [{'name': {'default': None, 'en': 'Laptop', 'fr': '…'}}]
            Product.objects.values('name')

            # Mix translatable and non-translatable fields
            Product.objects.values('id', 'name', 'price')
        """
        if not fields:
            # No field list supplied — standard Django behaviour.
            return super().values(*fields, **expressions)

        new_fields = []
        new_expressions = expressions.copy()

        # Read the list of translatable field *base* names from the model.
        translate_fields = getattr(self.model, 'translate_fields', [])

        # Build language list: 'default' first, then every configured locale.
        languages = ['default'] + [code for code, _label in getattr(settings, 'LANGUAGES', [])]

        for field in fields:
            if field in translate_fields:
                # Build a JSONObject that collects all per-language columns.
                json_kwargs = {}
                for lang in languages:
                    # Column naming convention mirrors i18nField.contribute_to_class:
                    #   <base>_default  for the fallback
                    #   <base>_<lang>   for every locale (hyphens → underscores)
                    col = f"{field}_default" if lang == 'default' else f"{field}_{lang.replace('-', '_')}"
                    json_kwargs[lang] = F(col)
                new_expressions[field] = JSONObject(**json_kwargs)
                # The original field name is now covered by the annotation;
                # do NOT add it to new_fields.
            else:
                new_fields.append(field)

        return super().values(*new_fields, **new_expressions)


class TranslatableQuerySet(TranslatableQuerySetMixin, models.QuerySet):
    """Concrete QuerySet with built-in translatable-field support.

    Combines :class:`TranslatableQuerySetMixin` with Django's standard
    :class:`~django.db.models.QuerySet`.  This is the class wired up by
    :class:`i18nutils.models.TranslatableModelMixin` via
    ``objects = TranslatableQuerySet.as_manager()``.

    You only need to reference this class directly if you are assigning the
    manager explicitly or calling ``as_manager()`` yourself.  For custom
    QuerySets, prefer mixing in :class:`TranslatableQuerySetMixin` instead.

    Example::

        class Product(TranslatableModelMixin, models.Model):
            objects = TranslatableQuerySet.as_manager()
    """
    # No additional logic needed: the mixin provides everything.
    pass
