"""testplatform URL Configuration

The `urlpatterns` list routes URLs to viewsx. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function viewsx
    1. Add an import:  from my_app import viewsx
    2. Add a URL to urlpatterns:  path('', viewsx.home, name='home')
Class-based viewsx
    1. Add an import:  from other_app.viewsx import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.common.urls')),
    path('', include('apps.automation.urls')),
    path('', include('apps.celery_task.urls')),
]
