import os
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings


schema_view = get_schema_view(
    openapi.Info(
        title="AllFlights API",
        default_version="v1",
        description="Documentation for AllFlights API endpoints.",
        contact=openapi.Contact(email='vicads01@gmail.com'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("app.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]

urlpatterns += staticfiles_urlpatterns()
if settings.ENVIRONMENT not in ("production", "staging"):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
