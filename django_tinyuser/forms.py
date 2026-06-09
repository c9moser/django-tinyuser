from django import forms
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import UploadedFile
# from django.contrib.auth import get_user_model
from django_tinyuser.models import TinyUserProfile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = TinyUserProfile
        fields = [
            'first_name',
            'last_name',
            'location',
            'website',
            'birth_date',
            'bio',
        ]

    def __init__(self, *args, **kwargs):
        avatar_small = kwargs.pop('avatar_small', None)
        avatar_medium = kwargs.pop('avatar_medium', None)
        avatar_large = kwargs.pop('avatar_large', None)
        avatar_full = kwargs.pop('avatar_full', None)

        super().__init__(*args, **kwargs)

        self.fields['avatar_small'] = forms.ImageField(
            label='Avatar (Small)',
            required=False,
            widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            initial=avatar_small
        )

        self.fields['avatar_medium'] = forms.ImageField(
            label='Avatar (Medium)',
            required=False,
            widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            initial=avatar_medium
        )

        self.fields['avatar_large'] = forms.ImageField(
            label='Avatar (Large)',
            required=False,
            widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            initial=avatar_large
        )

        self.fields['avatar_full'] = forms.ImageField(
            label='Avatar (Full)',
            required=False,
            widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            initial=avatar_full
        )

    def clean_avatar_small(self):
        "print the uploaded file for debugging purposes"
        avatar = self.cleaned_data.get('avatar_small')
        if avatar and isinstance(avatar, UploadedFile):
            if avatar.content_type not in ['image/jpeg', 'image/png']:
                raise forms.ValidationError("Only JPEG and PNG images are allowed.")
            if avatar.size > 2.5 * 1024 * 1024:  # Limit to 2.5MB
                raise forms.ValidationError("Avatar file size must be under 2.5MB.")
        elif avatar and not isinstance(avatar, ImageFile):
            raise forms.ValidationError("Invalid file type for avatar.")

        return avatar


class InviteForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=255)

    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if the email is already associated with an existing user
        if TinyUserProfile.objects.filter(user__email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
