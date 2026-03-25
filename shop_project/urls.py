from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth import views as auth_views
from store.forms import CustomLoginForm

from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),
]

urlpatterns += i18n_patterns(
    path('accounts/login/', auth_views.LoginView.as_view(authentication_form=CustomLoginForm), name='login'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(
        template_name='store/accounts/password_change.html',
        success_url=reverse_lazy('password_change_done')
    ), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='store/accounts/password_change_done.html'
    ), name='password_change_done'),
    path('', include('store.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
