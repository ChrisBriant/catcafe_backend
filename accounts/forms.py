# accounts/forms.py
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import Account
from catcafe.email import sendjoiningconfirmation
from catcafe.settings import BASE_URL

import random

def check_password(form,clearPassNoHash,chk):
    passed_check = True
    #Check that passwords match
    if clearPassNoHash != chk:
        msg = "The passwords must match"
        form.add_error('password',msg)
        passed_check = False

    #Minimum length
    if len(clearPassNoHash) < form.PASS_MIN_LENGTH:
        msg = "The new password must be at least %d characters long." % form.PASS_MIN_LENGTH
        form.add_error('password',msg)
        passed_check = False

    # At least one letter and one non-letter
    first_isalpha = clearPassNoHash[0].isalpha()
    if all(c.isalpha() == first_isalpha for c in clearPassNoHash):
        msg = "The new password must contain at least one letter and at least one digit or punctuation character."
        form.add_error('password',msg)
        passed_check = False
    return passed_check



class RegistrationForm(forms.ModelForm):
    PASS_MIN_LENGTH = 8
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    passwordchk = forms.CharField(label='Confirm', widget=forms.PasswordInput)
    class Meta:
        model = Account
        fields = ('email', 'name', 'password','passwordchk')

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.hash = hex(random.getrandbits(128))
        #Get joining confirmation information over to user
        #url = BASE_URL + "confirm/" + "/" + user.id + "/" + user.hash + "/?next=/add-listing"
        print(user.hash)
        url = BASE_URL + "confirm/" + user.hash + "/?next=/add-listing"
        sendjoiningconfirmation(url,user.name,user.email)
        if commit:
            user.save()
        return user


    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        clearPassNoHash = cleaned_data.get("password")
        chk = cleaned_data.get("passwordchk")
        if (check_password(self,clearPassNoHash,chk)):
            return cleaned_data
        else:
            raise ValidationError('Invalid registration details - Please check the details below')


class ConfirmRequestForm(forms.Form):
    email = forms.CharField(label='Email Address', widget=forms.EmailInput)


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'name', 'is_staff', 'is_superuser')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Account
        fields = ('email', 'name', 'date_of_birth', 'password', 'is_active', 'is_superuser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class ChangePasswordForm(forms.Form):
    PASS_MIN_LENGTH = 8
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    passwordchk = forms.CharField(label='Confirm', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        clearPassNoHash = cleaned_data.get("password")
        chk = cleaned_data.get("passwordchk")
        check_password(self,clearPassNoHash,chk)
        return cleaned_data


class NewPasswordForm(forms.Form):
    PASS_MIN_LENGTH = 8
    oldpassword = forms.CharField(label='Old Password', widget=forms.PasswordInput)
    password = forms.CharField(label='New Password', widget=forms.PasswordInput)
    passwordchk = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)
    user = None

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        super(NewPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewPasswordForm, self).clean()
        if not self.user.check_password(cleaned_data.get('oldpassword')):
            self.add_error('oldpassword','Your old password does not match')
        clearPassNoHash = cleaned_data.get("password")
        chk = cleaned_data.get("passwordchk")
        check_password(self,clearPassNoHash,chk)
        return cleaned_data
