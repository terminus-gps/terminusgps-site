from django.urls import path

from . import views

urlpatterns = [
    path("", views.TrackerProfileView.as_view(), name="tracker profile"),
    path("about/", views.TrackerAboutView.as_view(), name="tracker about"),
    path("contact/", views.TrackerContactView.as_view(), name="tracker contact"),
    path("source/", views.TrackerSourceView.as_view(), name="tracker source"),
    path("privacy/", views.TrackerPrivacyView.as_view(), name="tracker privacy"),
    path("login/", views.TrackerLoginView.as_view(), name="tracker login"),
    path("logout/", views.TrackerLogoutView.as_view(), name="tracker logout"),
    path("register/", views.TrackerRegistrationView.as_view(), name="tracker register"),
    path(
        "subscriptions/",
        views.TrackerSubscriptionView.as_view(),
        name="tracker subscriptions",
    ),
    path(
        "profile/assets/",
        views.TrackerProfileAssetsView.as_view(),
        name="profile assets",
    ),
    path(
        "profile/payments/",
        views.TrackerProfilePaymentMethodsView.as_view(),
        name="profile payments",
    ),
    path(
        "profile/subscription/",
        views.TrackerProfileSubscriptionView.as_view(),
        name="profile subscription",
    ),
    path(
        "profile/notifications/",
        views.TrackerProfileNotificationsView.as_view(),
        name="profile notifications",
    ),
]
