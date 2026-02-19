import logging
from django.db import models
from django.db.models import F
from django.db.models.functions import JSONObject
from django.conf import settings

logger = logging.getLogger(__name__)

class TranslatableQuerySet(models.QuerySet):
    def values(self, *fields, **expressions):
        """
        Overridden to handle translatable fields.
        If a field is in translate_fields, it's replaced by a JSON object
        containing all translations.
        """
        if not fields:
            # If no fields specified, standard behavior returns all fields.
            # We might want to handle this case too, but user specifically asked for
            # "se il campo richiesto in values e in translates_fields"
            return super().values(*fields, **expressions)

        new_fields = []
        new_expressions = expressions.copy()
        
        # Access translate_fields from the model
        translate_fields = getattr(self.model, 'translate_fields', [])
        
        # Get configured languages
        languages = ['default'] + [x[0] for x in getattr(settings, 'LANGUAGES', [])]

        for field in fields:
            if field in translate_fields:
                # Construct JSON object for the translatable field
                json_data = {}
                for lang in languages:
                    # Construct the actual field name for the language
                    # This logic must match how fields are created in fields.py
                    if lang == 'default':
                        lang_field = f"{field}_default"
                    else:
                        lang_field = f"{field}_{lang.replace('-', '_')}"
                    
                    json_data[lang] = F(lang_field)
                
                # Add the annotation
                new_expressions[field] = JSONObject(**json_data)
                # We don't add the original field name to new_fields because it's now an annotation/expression
            else:
                new_fields.append(field)
        
        return super().values(*new_fields, **new_expressions)
