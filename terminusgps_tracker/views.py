from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from terminusgps_tracker.models.wialon import WialonToken

from .decorators import requires_wialon_token
from .models import RegistrationForm
from .wialonapi import WialonQuery, WialonSession


def dashboard(request: HttpRequest) -> HttpResponse:
    wialon_token, created = WialonToken.objects.get_or_create(user=request.user)
    if created:
        return auth(request, "wialon")
    context = {
        "title": "Dashboard",
    }
    return render(request, "terminusgps_tracker/dashboard.html", context=context)


def auth(request: HttpRequest, service: str) -> HttpResponse:
    match service:
        case "wialon":
            token = WialonToken.objects.get_or_create(user=request.user)[0]
            context = {
                "title": "Wialon Authentication",
                "auth_url": token.auth_url,
            }
        case "lightmetrics":
            raise NotImplementedError
        case _:
            return HttpResponse(status=400)
    return render(request, "terminusgps_tracker/auth.html", context=context)


def oauth2_callback(request: HttpRequest, service: str) -> HttpResponse:
    user = request.user
    match service:
        case "wialon":
            token = WialonToken.objects.get(user=user)
            token.access_token = request.GET.get("access_token")
            token.username = request.GET.get("user_name")
            token.save()

        case "lightmetrics":
            raise NotImplementedError

        case _:
            return HttpResponse(status=400)

    context = {
        "user": user,
        "token": token,
        "service": service,
    }

    return render(request, "terminusgps_tracker/oauth2_callback.html", context=context)


def registration(request: HttpRequest, step: str) -> HttpResponse:
    if request.method == "POST":
        form = RegistrationForm(request.POST)
    else:
        form = RegistrationForm()

    context = {
        "title": "Registration",
        "form": form,
        "step": step,
    }
    return render(request, "terminusgps_tracker/register/form.html", context=context)


@requires_wialon_token
def search_wialon(request: HttpRequest) -> HttpResponse:
    token = WialonToken.objects.get(user=request.user).access_token
    with WialonSession(token=token) as session:
        query = WialonQuery(prop_name="sys_user")
        items = query.execute(session).get("items", [])
        context = {
            "title": "Search Results",
            "items": items,
        }
    return render(request, "terminusgps_tracker/search_wialon.html", context=context)


@requires_wialon_token
def search(request: HttpRequest) -> HttpResponse:
    search = request.POST.get("search", "*")
    token = WialonToken.objects.get(user=request.user).access_token
    with WialonSession(token=token) as session:
        query = WialonQuery()
        query.prop_value_mask = search
        items = query.execute(session).get("items", [])
    context = {
        "items": items,
    }
    return render(request, "terminusgps_tracker/_wialon_results.html", context=context)