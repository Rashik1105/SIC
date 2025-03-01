from django import forms
from django.contrib.auth.models import User
from .models import BusinessProfile,YoutubeUser

class BusinessRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()

    class Meta:
        model = BusinessProfile
        fields = ["business_name", "business_email", "business_category", "phone_number", "website"]

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
            email=self.cleaned_data["email"]
        )
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