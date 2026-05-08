from django.utils import translation

class ForceEnglishAdminMiddleware:
    """
    Middleware to force English language in the Django admin interface
    regardless of the user's frontend language preference.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            translation.activate('en')
            request.LANGUAGE_CODE = 'en'
            
        response = self.get_response(request)
        return response
