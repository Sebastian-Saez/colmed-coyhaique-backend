"""backend_colmed URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from base_colmed.views import GoogleLogin, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/colmed/', include('base_colmed.urls')),
    path('api/medicos/', include('base_medicos.urls')),
    path('api/noticias/', include('base_noticias.urls')),
    

    path('api/auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/', include('allauth.urls')),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
