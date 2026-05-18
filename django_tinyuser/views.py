from django.shortcuts import render
from django.views import View
from django_tinyuser import settings
INDEX_TEMPLATE = 'django_tinyuser/html/index.html'
if settings.CSS_FRAMEWORK == 'bootstrap':
    INDEX_TEMPLATE = 'django_tinyuser/bootstrap/index.html'
elif settings.CSS_FRAMEWORK == 'tailwindcss':
    INDEX_TEMPLATE = 'django_tinyuser/tailwindcss/index.html'


class IndexView(View):
    template_name = INDEX_TEMPLATE

    def get(self, request):
        return render(request, self.template_name)
