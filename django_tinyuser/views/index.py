from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from django_templates import get_template


class IndexView(View):
    """
    View for the index page.
    """

    # Define the template name for the index page using the TEMPLATE_MAPPING from settings
    template_name = get_template("tinyuser/index")

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handle GET requests to the index page.

        :param request: The HTTP request object.
        :type request: HttpRequest
        :return: The HTTP response object with the rendered template.
        :rtype: HttpResponse
        """
        return render(request, self.template_name)
