import decimal
from django import template
from django.utils import translation
from django.conf import settings

register = template.Library()

@register.filter(name='currency')
def currency(value, currency_code=None):
    if value is None:
        return ""
    
    try:
        # Convert to Decimal if it's not already
        if not isinstance(value, decimal.Decimal):
            value = decimal.Decimal(str(value))
            
        if currency_code:
            # Find settings by currency code
            currency_settings = next((v for v in settings.CURRENCIES.values() if v['code'] == currency_code), None)
            if not currency_settings:
                # Fallback to language if code not found
                language = translation.get_language()
                currency_settings = settings.CURRENCIES.get(language, settings.CURRENCIES.get('uk'))
        else:
            language = translation.get_language()
            currency_settings = settings.CURRENCIES.get(language, settings.CURRENCIES.get('uk'))
            
        rate = decimal.Decimal(str(currency_settings['rate']))
        symbol = currency_settings['symbol']
        
        converted_value = value * rate
        
        # Round to 2 decimal places
        converted_value = converted_value.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
        
        # Format based on symbol/currency
        if symbol == 'грн' or symbol == 'Kč':
            return f"{converted_value} {symbol}"
        else: # USD and others
            return f"{symbol}{converted_value}"
            
    except (ValueError, decimal.InvalidOperation):
        return value

@register.simple_tag
def get_currency_symbol(currency_code=None):
    if currency_code:
        currency_settings = next((v for v in settings.CURRENCIES.values() if v['code'] == currency_code), None)
        if currency_settings:
            return currency_settings['symbol']
            
    language = translation.get_language()
    currency_settings = settings.CURRENCIES.get(language, settings.CURRENCIES.get('uk'))
    return currency_settings['symbol']
