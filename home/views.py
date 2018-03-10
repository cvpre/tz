from django.shortcuts import render
from django.utils.translation import gettext as _


def e_handler404(request):
    context = {'message': _("Not found.")}
    response = render(request, 'home/404.html', context=context, status=404)
    return response


def e_handler500(request):
    context = {'message': _("Internal server error.")}
    response = render(request, 'home/500.html', context=context, status=500)
    return response


def csrf_failure(request, reason=""):
    context = {'message': _("CSRF token validation failed.")}
    return render(request, 'home/403.html', context=context, status=403)
