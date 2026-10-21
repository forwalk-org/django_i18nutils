import threading
from django.apps import AppConfig
from django.contrib import admin


class I18nUtilsConfig(AppConfig):
    name = 'i18nutils'
    verbose_name = 'i18n Utilities'

    def ready(self):
        from . import fields

        # Monkey-patch Django's ModelAdmin to track when we're in admin context
        original_formfield_for_dbfield = admin.ModelAdmin.formfield_for_dbfield

        def patched_formfield_for_dbfield(self, db_field, **kwargs):
            fields._admin_context.in_admin = True
            try:
                return original_formfield_for_dbfield(self, db_field, **kwargs)
            finally:
                fields._admin_context.in_admin = False

        admin.ModelAdmin.formfield_for_dbfield = patched_formfield_for_dbfield
