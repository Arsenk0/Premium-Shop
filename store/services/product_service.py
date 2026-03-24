import decimal
from decimal import Decimal
from django.conf import settings
from django.utils.translation import get_language

class ProductFilterService:
    @staticmethod
    def apply_filters(queryset, request_data, session, language=None):
        if not language:
            language = get_language()

        min_price = request_data.get('min_price')
        max_price = request_data.get('max_price')
        size_filter = request_data.get('size')
        in_stock = request_data.get('in_stock')
        sort = request_data.get('sort')

        if min_price or max_price:
            try:
                selected_currency = session.get('currency')
                if selected_currency:
                    currency_settings = next((v for v in settings.CURRENCIES.values() if v['code'] == selected_currency), None)
                else:
                    currency_settings = settings.CURRENCIES.get(language, settings.CURRENCIES.get('uk'))
                
                if not currency_settings:
                    currency_settings = settings.CURRENCIES.get('uk')

                rate = Decimal(str(currency_settings['rate']))
                
                if min_price and min_price.strip():
                    converted_min = Decimal(min_price) / rate
                    queryset = queryset.filter(price__gte=converted_min)
                if max_price and max_price.strip():
                    converted_max = Decimal(max_price) / rate
                    queryset = queryset.filter(price__lte=converted_max)
            except (ValueError, decimal.InvalidOperation, TypeError):
                pass
        
        if size_filter:
            queryset = queryset.filter(sizes__name=size_filter)

        if in_stock == '1':
            queryset = queryset.filter(stock__gt=0)

        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'name_asc':
            queryset = queryset.order_by('name')
        elif sort == 'name_desc':
            queryset = queryset.order_by('-name')
        else:
            queryset = queryset.order_by('-created')
            
        return queryset
