from django.db import models
from i18nutils.models import TranslatableModelMixin
from i18nutils.fields import i18nField

class Product(TranslatableModelMixin, models.Model):
    """
    Product model with translatable fields using i18nField.
    """
    name = i18nField(models.CharField(max_length=255, null=True, default=None))
    description = i18nField(models.TextField(null=True, default=None))

    def __str__(self):
        return str(self.name)

