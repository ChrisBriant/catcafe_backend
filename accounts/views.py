from django.shortcuts import render

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.utils.http import urlsafe_base64_decode
from django.middleware import csrf
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse


from .models import Account
from .forms import RegistrationForm, ConfirmRequestForm,ChangePasswordForm,NewPasswordForm
from catcafe.email import sendpasswordresetemail
from catcafe.settings import BASE_URL
import random


class RegistrationView(CreateView):
    template_name = 'registration/register.html'
    form_class = RegistrationForm

    def get_context_data(self, *args, **kwargs):
        context = super(RegistrationView, self).get_context_data(*args, **kwargs)
        context['next'] = self.request.GET.get('next')
        return context

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        success_url = reverse('login')
        messages.success(self.request,"You have successfully registered, please check your email for to confirm your registration")
        if next_url:
            success_url += '?next={}'.format(next_url)

        return success_url


class ProfileView(UpdateView):
    model = Account
    fields = ['name', 'phone', 'date_of_birth']
    template_name = 'registration/profile.html'

    def get_success_url(self):
        return reverse('index')

    def get_object(self):
        return self.request.user


# def confirm(request,hash):
#     try:
#         user = Account.objects.get(hash=hash)
#         user.is_enabled = True
#         user.save()
#         success = True
#     except Exception as e:
#         success = False
#         messages.error(request,"Something went wrong, please send a new password reset request")
#     return render(request,'registration/confirm.html',{'success' : success, 'show_header' : True, 'login_url' : BASE_URL })


def login(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        if user:
            if user.is_enabled:
                auth_login(request,user)
                return HttpResponseRedirect(next_url)
        else:
            messages.error(request,'username or password not correct')
            return redirect(reverse('login')+'?next={}'.format(next_url))
    else:
        form = AuthenticationForm()
    return render(request,'registration/login.html',{'form':form})


def passreset(request):
    form = ConfirmRequestForm()
    if request.POST:
        form = ConfirmRequestForm(request.POST)
        if form.is_valid():
            try:
                #Get the user
                user = Account.objects.get(email=form.cleaned_data["email"])
                #Create new conf object and email user
                hash = hex(random.getrandbits(128))
                user.hash = hash
                user.save()
                #Send registration confirmation
                url = BASE_URL + "password_reset_change/"+hash
                sendpasswordresetemail(url,user.name,user.email)
                messages.info(request,"Account confirmation has been resent to " + user.email + " please check your inbox for the confirmation link")
            except Exception as e:
                print(e)
                messages.error(request, "Sorry that account cannot be found")
        else:
            print(form.errors)
            messages.error(request, form.errors)
    return render(request, 'registration/password_reset_form.html', {'form' : form })

def passreset_api(request,hash):
    form = ChangePasswordForm()
    if request.POST:
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            try:
                user = Account.objects.get(hash=hash)
                user.set_password(form.cleaned_data['password'])
                user.is_enabled = True
                #Change the hash for security
                user.hash = hex(random.getrandbits(128))
                user.save()
                messages.info(request,"Your password has successfully been reset")
                return HttpResponseRedirect('/accounts/login/?next=/add-listing')
            except Exception as e:
                print(e)
                messages.error(request,"Sorry a matching account cannot be found")
        else:
            pass
            #messages.error(request,form.errors)
    return render(request, 'registration/password_reset_api.html', {'form' : form, 'show_header' : True, 'login_url' : BASE_URL })



def changepass_reset(request,hash):
    form = ChangePasswordForm()
    if request.POST:
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            try:
                user = Account.objects.get(hash=hash)
                user.set_password(form.cleaned_data['password'])
                user.is_enabled = True
                #Change the hash for security
                user.hash = hex(random.getrandbits(128))
                user.save()
                messages.info(request,"Your password has successfully been reset")
                return HttpResponseRedirect('/accounts/login/?next=/add-listing')
            except Exception as e:
                print(e)
                messages.error(request,"Sorry a matching account cannot be found")
        else:
            pass
            #messages.error(request,form.errors)
    return render(request,'registration/password_reset_form.html', {'form' : form })

#When user is LOGGED IN
def changepass(request):
    user = request.user
    if user.is_authenticated:
        form = NewPasswordForm()
        if request.POST:
                form = NewPasswordForm(request.POST,user=user)
                if form.is_valid():
                    try:
                        print("doing password change")
                        user.set_password(form.cleaned_data['password'])
                        user.save()
                        auth_login(request,user)
                        messages.info(request,"Your password has successfully been reset")
                        return HttpResponseRedirect(reverse('home'))
                    except Exception as e:
                        messages.error(request,"Unable to change password")
        else:
            pass
            #messages.error(request,form.errors)
    else:
        return HttpResponseRedirect('/accounts/login/?next=/add-listing')
    return render(request,'registration/password_change_form.html', {'form' : form })


def confirm(request,hash):
    next_url = request.GET.get('next')
    print(hash)
    print(next_url)
    try:
        user = Account.objects.get(hash=hash)
        user.is_enabled = True
        user.save()
        message = 'Login verified succesfully. You can now sign in.'
    except Exception as e:
        message = 'Unable to verify account, please try a forgot password reset.'
    return render(request,'accounts/confirmation.html',{'message':message})
