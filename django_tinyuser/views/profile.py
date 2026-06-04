from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from django_tinyuser.settings import TEMPLATE_MAPPING
from django_tinyuser.models import TinyUserProfile
from django_tinyuser.forms import ProfileForm
from django_tinyuser.mixins.htmx import HtmxMixin


class ProfileView(LoginRequiredMixin, HtmxMixin, FormView):
    """
    View for the user profile page.
    """

    #: Defines the template name for the profile page using the TEMPLATE_MAPPING from settings
    template_name = TEMPLATE_MAPPING['tinyuser/profile']
    htmx_template_name = TEMPLATE_MAPPING['tinyuser/hx/profile']

    #: Defines the form class for the profile view
    form_class = ProfileForm

    def get_context_data(self, **kwargs):
        """
        Retrieves the context data for the profile view.

        :return: Context data for the template
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        context['profile'] = self.instance
        if 'form' in kwargs:
            context['form'] = kwargs['form']
        else:
            context['form'] = self.form_class(instance=self.instance)
        return context

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handles GET requests for the profile view.

        :param request: The HTTP request object
        :type request: HttpRequest
        :return: The HTTP response with the rendered template
        :rtype: HttpResponse
        """
        self.instance = TinyUserProfile.objects.get_or_create(user=request.user)[0]
        print(f"Profile instance for user {request.user.username}: {self.instance}")
        return render(
            request,
            self.htmx_template_name if self.is_htmx_request else self.template_name,
            self.get_context_data()
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Handles POST requests for the profile view.

        :param request: The HTTP request object
        :type request: HttpRequest
        :return: The HTTP response with the rendered template
        :rtype: HttpResponse
        """
        self.instance = TinyUserProfile.objects.get_or_create(user=request.user)[0]
        form = self.form_class(request.POST, instance=self.instance)
        if form.is_valid():
            form.save(commit=True)
            self.instance.refresh_from_db()  # Refresh the instance to get the updated data
            context = self.get_context_data()
            context['success'] = True
            return render(
                request,
                self.htmx_template_name if self.is_htmx_request else self.template_name,
                context
            )
        context = self.get_context_data()
        context['form'] = form
        return render(
            request,
            self.htmx_template_name if self.is_htmx_request else self.template_name,
            context
        )
