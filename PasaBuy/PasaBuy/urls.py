"""
URL configuration for PasaBuy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from main.views import (
    browser,
    accept_order,
    cancel_order,
    complete_order,
    hero_page,
    index,
    logout_view,
    my_orders,
    info_page,
    order_detail,
    order_page,
    signup_complete,
    signup_details,
    upload_id,
    user_page,
)

urlpatterns = [
    path('', index, name='index'),
    path('signup/details/', signup_details, name='signup_details'),
    path('signup/complete/', signup_complete, name='signup_complete'),
    path('logout/', logout_view, name='logout'),
    path('hero/', hero_page, name='hero'),
    path('browser/', browser, name='browser'),
    path('my-orders/', my_orders, name='my_orders'),
    path('order/', order_page, name='order_page'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('order/<int:order_id>/accept/', accept_order, name='accept_order'),
    path('order/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
    path('order/<int:order_id>/complete/', complete_order, name='complete_order'),
    path('profile/', user_page, name='user_page'),
    path('info/', info_page, name='info_page'),
    path('upload-id/', upload_id, name='upload_id'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
