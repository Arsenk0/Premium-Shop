from django.test import TestCase, override_settings
from django.template import Context, Template
from django.urls import reverse
from django.utils import translation
from decimal import Decimal
from django.conf import settings

class CurrencyFilterTest(TestCase):
    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def test_currency_conversion_uk(self):
        with translation.override('uk'):
            rendered = self.render_template(
                '{% load currency_tags %}{{ price|currency }}',
                {'price': Decimal('100.00')}
            )
            # rate 1.0 -> 100.00 грн
            self.assertEqual(rendered, '100.00 грн')

    def test_currency_conversion_en(self):
        with translation.override('en'):
            rendered = self.render_template(
                '{% load currency_tags %}{{ price|currency }}',
                {'price': Decimal('100.00')}
            )
            # rate 0.024 -> 2.40 -> $2.40
            self.assertEqual(rendered, '$2.40')

    def test_currency_conversion_cs(self):
        with translation.override('cs'):
            rendered = self.render_template(
                '{% load currency_tags %}{{ price|currency }}',
                {'price': Decimal('100.00')}
            )
            # rate 0.55 -> 55.00 -> 55.00 Kč
            self.assertEqual(rendered, '55.00 Kč')

    def test_currency_invalid_value(self):
        rendered = self.render_template(
            '{% load currency_tags %}{{ price|currency }}',
            {'price': 'not-a-number'}
        )
        self.assertEqual(rendered, 'not-a-number')

    def test_currency_none_value(self):
        rendered = self.render_template(
            '{% load currency_tags %}{{ price|currency }}',
            {'price': None}
        )
        self.assertEqual(rendered, '')

    def test_currency_explicit_code(self):
        rendered = self.render_template(
            '{% load currency_tags %}{{ price|currency:"USD" }}',
            {'price': Decimal('100.00')}
        )
        # rate 0.024 -> $2.40
        self.assertEqual(rendered, '$2.40')

    def test_get_currency_symbol_explicit(self):
        rendered = self.render_template(
            '{% load currency_tags %}{% get_currency_symbol "CZK" %}'
        )
        self.assertEqual(rendered, 'Kč')

class CurrencyViewTest(TestCase):
    def test_set_currency(self):
        # We need a language prefix because of i18n_patterns
        url = reverse('store:set_currency')
        response = self.client.post(url, {'currency': 'USD', 'next': '/'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['currency'], 'USD')

    def test_set_currency_invalid(self):
        url = reverse('store:set_currency')
        response = self.client.post(url, {'currency': 'INVALID', 'next': '/'})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('currency', self.client.session)
