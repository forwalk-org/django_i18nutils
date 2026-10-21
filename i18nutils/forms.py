import copy
from typing import List, Tuple, Optional, Union

from django import forms
from django.conf import settings
from django.forms.widgets import Input

from .utils import i18nString


class TextInput(Input):
    input_type = "text"
    template_name = "i18n/widgets/input.html"

    def __init__(self, language: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = language

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context["language"] = self.language
        return context


class TextArea(TextInput):
    template_name = "i18n/widgets/textarea.html"

    def __init__(self, language: str, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        default_attrs = {"cols": "40", "rows": "10"}
        if attrs:
            default_attrs.update(attrs)
        kwargs["attrs"] = default_attrs
        super().__init__(language, *args, **kwargs)


class I18nWidget(forms.MultiWidget):
    """
    The default form widget for JSONi18nCharField and JSONi18nTextField. It makes
    use of Django's MultiWidget mechanism.
    """
    widget = TextInput

    def __init__(
        self,
        locales: Optional[List[Tuple[str, str]]] = None,
        field: Optional[forms.Field] = None,
        attrs=None,
    ):
        widgets = []
        if locales is None:
            # Reconstruct locales from settings if not passed
            langs = [('default', 'Default')] + list(getattr(settings, 'LANGUAGES', []))
            self.locales = langs
        else:
            self.locales = locales
            
        self.enabled_locales = self.locales
        self.field = field
        
        for code, language in self.locales:
            a = copy.copy(attrs) or {}
            a["lang"] = code
            widgets.append(self.widget(language=language, attrs=a))
        super().__init__(widgets, attrs)

    def decompress(self, value) -> List[Optional[str]]:
        data: List[Optional[str]] = []
        if not value:
            return [None] * len(self.locales)

        if not isinstance(value, i18nString):
            value = i18nString(value)

        # Get exact translations without fallback logic
        exact_translations = value.get_translations()

        for i, locale in enumerate(self.locales):
            lng = locale[0]
            exact_val = exact_translations.get(lng)
            data.append(exact_val)

        return data

    def render(self, name: str, value, attrs=None, renderer=None) -> str:
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
                
        if not isinstance(value, list) and value is not None:
            value = self.decompress(value)
        elif value is None:
            value = [None] * len(self.locales)
            
        final_attrs = self.build_attrs(attrs or dict())
        id_ = final_attrs.get("id", None)
        
        from django.utils.safestring import mark_safe
        
        output = []
        for i, widget in enumerate(self.widgets):
            locale = self.locales[i]
            lang = locale[0]

            if locale not in self.enabled_locales:
                continue
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
                
            if id_:
                final_attrs = dict(final_attrs, id="%s_%s" % (id_, i), title=lang)
            
            rendered_field = widget.render(
                name + "_%s" % i, widget_value, final_attrs, renderer=renderer
            )
            
            output.append(
                f'<div class="i18n-lang-container" data-i18n-lang="{lang}">'
                f'{rendered_field}'
                f'</div>'
            )

        return mark_safe(self.format_output(name, output))

    def format_output(self, name: str, rendered_widgets: List[str]) -> str:
        html = f"""
        <div id="i18n-wrapper-{name}" class="i18n-form-group">
            {"".join(rendered_widgets)}
        </div>
        """
        return html


class I18nTextInput(I18nWidget):
    widget = TextInput

class I18nTextarea(I18nWidget):
    widget = TextArea


# --- Advanced Widgets for Django Admin ---

class I18nAdminWidget(I18nWidget):
    """
    Advanced widget for Django Admin, providing a select dropdown to switch languages
    using vanilla JS defined in an external static file.
    """
    class Media:
        css = {
            'all': ('i18nutils/css/i18n_admin_widget.css',)
        }
        js = ('i18nutils/js/i18n_admin_widget.js',)

    def format_output(self, name: str, rendered_widgets: List[str]) -> str:
        # Build language selector
        select_options = []
        for locale in self.locales:
            select_options.append(f'<option value="{locale[0]}">{locale[1]}</option>')
        select_html = f'<select class="i18n-lang-selector">{"".join(select_options)}</select>'

        html = f"""
        <div id="i18n-wrapper-{name}" class="i18n-form-group admin-advanced">
            <span class="i18n-lang-selector-label">Language to edit/insert:</span>
            {select_html}
            {"".join(rendered_widgets)}
        </div>
        """
        return html

class I18nAdminTextInput(I18nAdminWidget):
    class AdminInput(TextInput):
        template_name = "i18n/widgets/admin_input.html"
    
    widget = AdminInput
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for w in self.widgets:
            existing_class = w.attrs.get('class', '')
            w.attrs['class'] = f"{existing_class} vTextField".strip()

class I18nAdminTextarea(I18nAdminWidget):
    class AdminTextArea(TextArea):
        template_name = "i18n/widgets/admin_textarea.html"
        
    widget = AdminTextArea
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for w in self.widgets:
            existing_class = w.attrs.get('class', '')
            w.attrs['class'] = f"{existing_class} vLargeTextField".strip()


class I18nFormField(forms.MultiValueField):
    """
    The form field that is used by JSONi18nCharField and JSONi18nTextField.
    """
    def compress(self, data_list) -> i18nString:
        locales = self.locales
        data = {}
        for i, value in enumerate(data_list):
            if value:
                data[locales[i][0]] = value
        return i18nString(data)

    def clean(self, value) -> i18nString:
        found = False
        found_all = True
        clean_data = []
        errors: List[str] = []

        # If value is already an i18nString (e.g. initial disabled field), decompose it
        if isinstance(value, i18nString):
            value = self.widget.decompress(value)

        if value is None:
            value = []

        for i, field in enumerate(self.fields):
            try:
                field_value = value[i]
            except (IndexError, TypeError):
                field_value = None
            if field_value not in self.empty_values:
                found = True
            elif field.locale in getattr(self.widget, 'enabled_locales', self.locales):
                found_all = False
            try:
                clean_data.append(field.clean(field_value))
            except forms.ValidationError as e:
                errors.extend(m for m in e.error_list if m not in errors)
                
        if errors:
            raise forms.ValidationError(errors)
        if self.one_required and not found:
            raise forms.ValidationError(self.error_messages["required"], code="required")
        if self.require_all_fields and not found_all:
            raise forms.ValidationError(self.error_messages["incomplete"], code="incomplete")

        out = self.compress(clean_data)
        self.validate(out)
        self.run_validators(out)
        return out

    def __init__(self, *args, **kwargs):
        fields = []
        defaults = {"widget": self.widget, "max_length": kwargs.pop("max_length", None)}
        
        # Default locales to settings.LANGUAGES
        settings_langs = [('default', 'Default')] + list(getattr(settings, 'LANGUAGES', []))
        self.locales = kwargs.pop("locales", settings_langs)
        
        self.one_required = kwargs.get("required", True)
        self.require_all_fields = kwargs.pop("require_all_fields", False)
        
        kwargs["required"] = False
        widget_class = kwargs.pop("widget", self.widget)
        
        if isinstance(widget_class, type):
            kwargs["widget"] = widget_class(
                locales=self.locales, field=self, **kwargs.pop("widget_kwargs", {})
            )
        
        # encoder and decoder are defaults for JSONField, not for CharField!
        kwargs.pop("encoder", None)
        kwargs.pop("decoder", None)

        defaults.update(**kwargs)
        base_label = defaults.get("label", "")
        for lngcode, lngname in self.locales:
            if base_label:
                defaults["label"] = f"{base_label} ({lngcode})"
            else:
                defaults["label"] = lngcode
            field = forms.CharField(**defaults)
            field.locale = lngcode
            fields.append(field)
            
        super().__init__(fields=fields, require_all_fields=False, *args, **kwargs)
