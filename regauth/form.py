from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class LogInForm(forms.Form):
    username = forms.CharField(label="Username:", min_length=4, max_length=25)
    password = forms.CharField(label="Password:", min_length=8, widget=forms.PasswordInput)


class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label="Username:", min_length=4, max_length=25, validators=[
        RegexValidator(regex=r'^[0-9A-Za-z-_.]+$', message="Username has the wrong format!")],
                               help_text=["Letters, digits and ./-/_ only.",
                                          "Username must contain at least 4 characters."])
    email = forms.EmailField(label="Email:", help_text="my_email@example.com")
    password1 = forms.CharField(label="Password:", widget=forms.PasswordInput, strip=False,
                                help_text=["Password can't be too similar.",
                                           "Password must contain at least 8 characters.",
                                           "Password can't be entirely numeric."])
    password2 = forms.CharField(label="Password confirmation:", widget=forms.PasswordInput, strip=False,
                                help_text="Enter the same password as before, for verification.")

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        q = User.objects.filter(username=username)
        if q.count():
            raise ValidationError(_("Provided username already in use."), code='invalid')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError(_("Provided email already in use."), code='invalid')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 is not None and validate_password(password1) is None:
            if password1 and password2 and password1 != password2:
                raise ValidationError(_("The passwords do not match."), code='invalid')
        else:
            ValidationError(_(""), code='invalid')
        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        return user


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label=_("Your old password:"), strip=False,
                                   widget=forms.PasswordInput(attrs={'autofocus': True}))
    new_password1 = forms.CharField(label="New password:", widget=forms.PasswordInput, strip=False,
                                    help_text=["Password can't be too similar.",
                                               "Password must contain at least 8 characters.",
                                               "Password can't be entirely numeric."])
    new_password2 = forms.CharField(label="Password confirmation:", strip=False, widget=forms.PasswordInput,
                                    help_text="Enter the same password as before, for verification.")
