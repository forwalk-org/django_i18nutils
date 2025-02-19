import logging
from django.db import models

# Set up logging for debugging
logger = logging.getLogger(__name__)

class TranslatableModelMixin:
    """
    Mixin to add support for translatable fields in Django models.

    This mixin automatically tracks fields that should be treated as translatable.
    """

    translate_fields = []

    def __init__(self, *args, **kwargs):
        """
        Initialize a model instance, handling translatable fields.
        """
        # Collect values for translatable fields
        field_values = {field: kwargs.pop(field, None) for field in self.translate_fields if field in kwargs}

        # Call the parent constructor
        super().__init__(*args, **kwargs)

        # Set the values for each translatable field
        for field, value in field_values.items():
            if value is not None:
                setattr(self, field, value)  # Uses the i18nField setter logic if field is i18nField

    @classmethod
    def add_translate_field(cls, field_name: str):
        """
        Add a translatable field name to `translate_fields`.

        This method is called by `i18nField` to register itself in the model.
        """
        if field_name not in cls.translate_fields:
            cls.translate_fields.append(field_name)
            logger.debug("Added field '%s' to translate_fields", field_name)
