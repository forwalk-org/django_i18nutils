import logging
import json
import threading
from django.db.models.fields import Field
from django.db.models import JSONField
from .utils import i18nString
from .forms import I18nFormField, I18nTextInput, I18nTextarea, I18nAdminTextInput, I18nAdminTextarea

# Set up logging
logger = logging.getLogger(__name__)

# Thread-local storage for tracking Django Admin context
_admin_context = threading.local()


class i18nFieldMixin:
    """
    Mixin for JSON-based i18n fields.
    Stores all translations in a single JSON database column as an i18nString.
    """
    form_class = I18nFormField
    widget = I18nTextInput

    def to_python(self, value):
        if isinstance(value, i18nString):
            return value
        if value is None:
            return None
        if isinstance(value, dict):
            return i18nString(value)
        if isinstance(value, str):
            try:
                # Try parsing as JSON if it's a string, like from DB in old Django versions
                jval = json.loads(value)
                return i18nString(jval)
            except (ValueError, TypeError):
                pass
        return i18nString(value)

    def get_prep_value(self, value):
        if isinstance(value, i18nString):
            value = value._translations
        if isinstance(value, dict):
            # Strip empty strings and None values so fallback logic works correctly
            value = {k: v for k, v in value.items() if v is not None and v != ''}
        return super().get_prep_value(value)

    def validate(self, value, model_instance):
        # Convert i18nString to dict so JSONField's validate() doesn't fail on json.dumps
        if isinstance(value, i18nString):
            val = value._translations
        else:
            val = value
        super().validate(val, model_instance)

    def from_db_value(self, value, expression, connection, *args, **kwargs):
        return self.to_python(value)

    def formfield(self, **kwargs):
        is_admin = getattr(_admin_context, 'in_admin', False)

        if is_admin:
            from .forms import I18nAdminTextInput, I18nAdminTextarea
            is_textarea = issubclass(self.widget, I18nTextarea) if isinstance(self.widget, type) else False
            if is_textarea:
                defaults = {"form_class": self.form_class, "widget": I18nAdminTextarea}
            else:
                defaults = {"form_class": self.form_class, "widget": I18nAdminTextInput}
        else:
            defaults = {"form_class": self.form_class, "widget": self.widget}

        kwargs.pop('widget', None) # Override whatever widget was passed if any

        if hasattr(self, 'max_length') and self.max_length:
            defaults['max_length'] = self.max_length
        defaults.update(kwargs)
        # JSONField passes `encoder` and `decoder` kwargs that our form doesn't want
        kwargs.pop("encoder", None)
        kwargs.pop("decoder", None)
        return super().formfield(**defaults)


class i18nCharField(i18nFieldMixin, JSONField):
    """
    A CharField which takes internationalized data and stores it as JSON.
    Interaction with this field uses i18nString instances.
    """
    widget = I18nTextInput

    def __init__(self, *args, **kwargs):
        self.max_length = kwargs.get("max_length")
        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        if self.max_length is not None and not isinstance(self.max_length, int):
            from django.core import checks
            errors.append(
                checks.Error(
                    "'max_length' must be a positive integer.",
                    obj=self,
                    id='fields.E121',
                )
            )
        return errors

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        # Validate max_length on each translated string
        if self.max_length and isinstance(value, i18nString):
            from django.core.exceptions import ValidationError
            for lang, text in value.get_translations().items():
                if text and len(str(text)) > self.max_length:
                    raise ValidationError(
                        f"Value for language '{lang}' exceeds max_length of {self.max_length} characters."
                    )


class i18nTextField(i18nFieldMixin, JSONField):
    """
    Like i18nCharField, but for TextFields (uses a Textarea widget).
    """
    widget = I18nTextarea
