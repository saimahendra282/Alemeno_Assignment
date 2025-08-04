from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from core.views import landing_page

# Configure API schema view for Swagger and ReDoc
schema_view = get_schema_view(
    openapi.Info(
        title="credit approval system API by Sai Mahendra",
        default_version='v1',
        description="API documentation for the credit approval system",
        
        contact=openapi.Contact(email="bejawadasaimahendra@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Define main URL routes for admin panel, core APIs, and API docs
urlpatterns = [
     path('', landing_page, name='landing'),
    path('admin/', admin.site.urls),                               # Django admin interface
    path('api/', include('core.urls')),                            # Core app API endpoints
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),  # Raw Swagger schema
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),                 # Swagger UI docs
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),                         # ReDoc UI docs
]
