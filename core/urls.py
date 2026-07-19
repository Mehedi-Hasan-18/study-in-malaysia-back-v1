"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import include, path
from .views import api_root

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api_root, name='api-root'),
    path('api/v1/', include('accounts.urls')),
    path('api/v1/', include('common.urls')),
    path('api/v1/', include('universities.urls')),
    path('api/v1/', include('faculties.urls')),
    path('api/v1/', include('programs.urls')),
    path('api/v1/', include('intakes.urls')),
    path('api/v1/', include('tuition.urls')),
    path('api/v1/', include('scholarships.urls')),
    path('api/v1/', include('applications.urls')),
    path('api/v1/', include('documents.urls')),
    path('api/v1/', include('wishlist.urls')),
    path('api/v1/', include('news.urls')),
    path('api/v1/', include('dashboard.urls')),
    path('api/v1/', include('notifications.urls')),
]
