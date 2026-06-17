from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.views.generic import FormView
from django_templates import get_template

from django_tinyuser.forms import InviteForm
from django_tinyuser.logging import get_tinyuser_logger as get_logger
from django_tinyuser.settings import (
    INVITE_ALLOW_ALL_AUTHENTICATED_USERS,
    INVITE_GROUPS,
)

logger = get_logger(__name__)


class InviteView(UserPassesTestMixin, FormView):
    """
    View for the invite page.
    """

    #: Defines the template names for the invite page using the TEMPLATE_MAPPING from settings
    template_name = get_template("tinyuser/invite")

    #: Defines the template names for the success and failed states of the invite process
    success_template_name = get_template("tinyuser/invite/success")

    #: Defines the template name for the failed state of the invite process
    failed_template_name = get_template("tinyuser/invite/failed")

    #: Defines the template names for HTMX requests
    hx_template_name = get_template("tinyuser/hx/invite")

    #: Defines the template name for the success state of the invite process for HTMX requests
    hx_success_template_name = get_template("tinyuser/hx/invite/success")

    #: Defines the template name for the failed state of the invite process for HTMX requests
    hx_failed_template_name = get_template("tinyuser/hx/invite/failed")

    #: Defines the form class for the invite view
    form_class = InviteForm

    def test_func(self):
        """
        Determines whether the current user has permission to access the invite view.

        In this implementation, only authenticated users are allowed to access the invite view.

        :return: True if the user is authenticated, False otherwise.
        :rtype: bool
        """

        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                return True  # Allow superusers to access the invite view
            elif self.request.user.is_staff:
                return True  # Allow staff users to access the invite view
            else:
                if (
                    INVITE_GROUPS
                    and self.request.user.groups.filter(name__in=INVITE_GROUPS).exists()
                ):
                    # If no specific invite group is set, allow only superusers and staff to access the invite view
                    # except INVITE_ALLOW_ALL_AUTHENTICATED_USERS is set to True
                    return True
                elif INVITE_ALLOW_ALL_AUTHENTICATED_USERS:
                    # Allow all authenticated users to access the invite view
                    return True
        return False

    def get_context_data(self, **kwargs):
        """
        Retrieves the context data for the invite view.

        :return: Context data for the template
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        if "form" in kwargs:
            context["form"] = kwargs["form"]
        else:
            context["form"] = self.form_class()
        return context

    def get(self, request):
        """
        Handles GET requests for the invite view.

        :param request: The HTTP request object
        :type request: HttpRequest
        :return: The HTTP response with the rendered template
        :rtype: HttpResponse
        """
        return render(
            request,
            (self.hx_template_name if self.is_htmx_request else self.template_name),
            self.get_context_data(),
        )

    @property
    def is_htmx_request(self):
        """
        Checks if the current request is an HTMX request.

        :return: True if the current request is an HTMX request, False otherwise
        :rtype: bool
        """
        return self.request.headers.get("Hx-Request") == "true"

    def post(self, request):
        """
        Handles POST requests for the invite view.

        :param request: The HTTP request object
        :type request: HttpRequest
        :return: The HTTP response with the rendered template
        :rtype: HttpResponse
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            from invitations.utils import get_invitation_model

            email = form.cleaned_data["email"]
            # Here you would typically create an invitation and send an email
            Invitation = get_invitation_model()
            invitation = (
                Invitation.objects.filter(email__iexact=email)
                .order_by("created")
                .last()
            )

            if invitation is None:
                try:
                    # Do not use Invitation.objects.create ormessage.body,
                    # Invitation.objects.update_or_create, but use Invitation.create
                    # instead, because it sets the key to a secure random value
                    invitation = Invitation.create(email=email, inviter=request.user)

                    invitation.send_invitation(request)
                    context = self.get_context_data()
                    context["success"] = True
                    logger.info(f"Invitation sent to {email}")
                    return render(
                        request,
                        (
                            self.hx_success_template_name
                            if self.is_htmx_request
                            else self.success_template_name
                        ),
                        context,
                    )

                except Exception as e:
                    error_message = str(e)
                    context = self.get_context_data()
                    context["error"] = error_message
                    logger.error(
                        f"Failed to send invitation to {email}: {error_message}"
                    )

        context = self.get_context_data()
        context["form"] = form
        return render(
            request,
            (
                self.hx_failed_template_name
                if self.is_htmx_request
                else self.failed_template_name
            ),
            context,
        )
