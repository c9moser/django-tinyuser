from django import forms
# from django.contrib.auth import get_user_model
from django_tinyuser.models import TinyUserProfile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = TinyUserProfile
        fields = [
            'first_name',
            'last_name',
            'bio',
        ]  # No fields to edit, just a placeholder for the profile page


class InviteForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=255)

    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if the email is already associated with an existing user
        if TinyUserProfile.objects.filter(user__email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
