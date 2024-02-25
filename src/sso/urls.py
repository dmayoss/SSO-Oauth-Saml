import uniauth_saml2_idp.urls
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView, RedirectView
from two_factor.urls import urlpatterns as tf_urls

from users.views import home, GitLabApiUserView, GiteaApiUserView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # new
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("auth/", include("login.urls")),
    path("users/", include("users.urls")),
    path("staff/", include("staff.urls")),
    path("app/", include("appdb.urls")),
    path(
        "idp/",
        include(
            (
                uniauth_saml2_idp.urls,
                "uniauth_saml2_idp",
            )
        ),
    ),
    path("captcha/", include("captcha.urls")),
    path("", include("user_sessions.urls", "user_sessions")),
    path("", include(tf_urls)),
    path("", home, name="home"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),
    path("api/v3/user", GitLabApiUserView.as_view()),
    path("api/v4/user", GitLabApiUserView.as_view()),
    path("gitlab/user", GiteaApiUserView.as_view()),
    # path("terms/", include("termsandconditions.urls")),
]
