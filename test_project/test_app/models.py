from django.db import models
from i18nutils.fields import i18nCharField, i18nTextField


class Product(models.Model):
    """
    Product model with translatable fields stored as JSON.
    """
    name = i18nCharField(max_length=255, null=True, blank=True, db_index=True, help_text="This field will be interpolated in different languages. Enter the product name.")
    description = i18nTextField(null=True, blank=True, help_text="Detailed multilingual description that will appear in the catalog.")

    def __str__(self):
        return str(self.name)
