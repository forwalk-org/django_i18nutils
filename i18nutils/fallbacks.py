from enum import Enum

class FallbackStrategy(Enum):
    """
    Strategies available for translating an i18n string when the requested 
    language is not found. Strategies can optionally be called to pass
    parameters (e.g., FIRST_AVAILABLE('en', 'it', 'es')).
    """
    REGIONAL_VARIANT = 'regional_variant'
    DEFAULT_VALUE = 'default_value'
    FIRST_AVAILABLE = 'first_available'
    STATIC_VALUE = 'static_value'
    
    def __call__(self, *args):
        """Allows passing arguments to evaluate as a tuple (Strategy, args)"""
        return (self, args)
