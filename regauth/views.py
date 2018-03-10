from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _

from .form import CustomUserCreationForm, LogInForm, CustomPasswordChangeForm


def user_login(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            try:
                user_data = User.objects.get(username=form.cleaned_data.get('username'))
                user = authenticate(username=form.cleaned_data.get('username'),
                                    password=form.cleaned_data.get('password'))
            except User.DoesNotExist:
                messages.error(request, _("Invalid username/password or user does not exist."))
                return render(request, 'regauth/login.html', {'form': form})
            if user is not None:
                login(request, user)
                return redirect(request.POST.get('next', 'blog:index'))
    else:
        form = LogInForm()
    return render(request, 'regauth/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('blog:index')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            return redirect('regauth:user_login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'regauth/register.html', {'form': form})


@login_required(login_url='/auth/login/')
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _("Password has changed."))
            return redirect('regauth:change_password')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'regauth/change_password.html', {'form': form})