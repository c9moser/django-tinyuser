from dj_templates.mixins.theme import ThemeMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View


class IndexView(ThemeMixin, View):
    """
    View for the index page.
    """

    template_name = "@tinyuser/index"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.get_template_name(), context={})
