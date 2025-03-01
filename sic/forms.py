from django import forms
from django.contrib.auth.models import User
from .models import BusinessProfile,YoutubeUser
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

class BusinessRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    class Meta:
        model = BusinessProfile
        fields = ["business_name", "business_email", "business_category", "phone_number", "website"]

    def clean_email(self):
        """Ensure email is unique and normalized."""
        email = self.cleaned_data["business_email"].lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        """Create user and business profile securely."""
        email = self.cleaned_data["business_email"].lower().strip()  # Normalize email
        password = self.cleaned_data["password"]

        # Create user with email as username
        user = User.objects.create(
            username=email,  # Username is set to email
            email=email,
            password=make_password(password)  # Securely hash the password
        )

        # Create Business Profile
        business_profile = super().save(commit=False)
        business_profile.user = user

        if commit:
            business_profile.save()
        return business_profile

class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ["business_name", "business_email", "phone_number", "website", "business_category", "intrested_category"]

class YoutubeUserForm(forms.ModelForm):
    class Meta:
        model = YoutubeUser
        fields = ["owner_name", "phone_number", "channel_category", "keywords"]