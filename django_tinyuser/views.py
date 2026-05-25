from django.shortcuts import render
from django.views import View
# from django_tinyuser import settings
from django_tinyuser.models import TinyUserProfile
from django_tinyuser.forms import ProfileForm, InviteForm
from django.views.generic import FormView

from django_tinyuser.settings import TEMPLATE_MAPPING


class IndexView(View):
    template_name = TEMPLATE_MAPPING['tinyuser/index']

    def get(self, request):
        return render(request, self.template_name)


class ProfileView(FormView):
    template_name = TEMPLATE_MAPPING['tinyuser/profile']
    form_class = ProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.instance
        if 'form' in kwargs:
            context['form'] = kwargs['form']
        else:
            context['form'] = self.form_class(instance=self.instance)
        return context

    def get(self, request):
        self.instance = TinyUserProfile.objects.get_or_create(user=request.user)[0]
        print(f"Profile instance for user {request.user.username}: {self.instance}")
        return render(request, self.template_name, self.get_context_data())

    def post(self, request):
        self.instance = TinyUserProfile.objects.get_or_create(user=request.user)[0]
        form = self.form_class(request.POST, instance=self.instance)
        if form.is_valid():
            form.save(commit=True)
            self.instance.refresh_from_db()  # Refresh the instance to get the updated data
            context = self.get_context_data()
            context['success'] = True
            return render(request, self.template_name, context)
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)


class InviteView(FormView):
    template_name = TEMPLATE_MAPPING['tinyuser/invite']
    success_template_name = TEMPLATE_MAPPING['tinyuser/invite-success']
    failed_template_name = TEMPLATE_MAPPING['tinyuser/invite-failed']
    hx_template_name = TEMPLATE_MAPPING['tinyuser/hx/invite']
    hx_success_template_name = TEMPLATE_MAPPING['tinyuser/hx/invite-success']
    hx_failed_template_name = TEMPLATE_MAPPING['tinyuser/hx/invite-failed']

    form_class = InviteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' in kwargs:
            context['form'] = kwargs['form']
        else:
            context['form'] = self.form_class()
        return context

    def get(self, request):
        return render(
            request,
            (
                self.hx_template_name
                if self.is_htmx_request
                else self.template_name
            ),
            self.get_context_data())

    @property
    def is_htmx_request(self):
        return self.request.headers.get('Hx-Request') == 'true'

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            from invitations.utils import get_invitation_model

            email = form.cleaned_data['email']
            # Here you would typically create an invitation and send an email
            Invitation = get_invitation_model()
            invitation = (Invitation.objects
                          .filter(email__iexact=email)
                          .order_by('created')
                          .last())

            if invitation is None:
                try:
                    # Do not use Invitation.objects.create or
                    # Invitation.objects.update_or_create, but use Invitation.create
                    # instead, because it sets the key to a secure random value
                    invitation = Invitation.create(email=email, inviter=request.user)

                    invitation.send_invitation(request)
                    context = self.get_context_data()
                    context['success'] = True
                    return render(
                        request,
                        (
                            self.hx_success_template_name
                            if self.is_htmx_request
                            else self.success_template_name
                        ),
                        context
                    )
                except Exception as e:
                    error_message = str(e)
                    context = self.get_context_data()
                    context['error'] = error_message

        context = self.get_context_data()
        context['form'] = form
        return render(
            request,
            (
                self.hx_failed_template_name
                if self.is_htmx_request
                else self.failed_template_name
            ),
            context
        )
