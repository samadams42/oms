"""untitled2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf.urls import url
from django.urls import path

from reallytired.views import *


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('reg_success', login_new, name='login_new'),
    path('login/', login_view, name='login_vw'),
    path('logout/', logout_view, name='logout_vw'),
    path('register/', reg_view, name='register_vw'),
    path('', index, name='index'),
    path('inventory/', inventory, name='inventory'),
    path('inventory/add', inv_add, name='inv_add'),
    path('export_csv/', inv_export, name='export_csv'),
    path('inventory/edit/<int:partId>/', inv_edit, name='inv_edit'),
    path('inventory/details/<int:partId>/', inv_details, name='inv_details'),
    path('inventory/delete/<int:partId>/', inv_delete, name='inv_delete'),
    path('orders/', orders, name='orders'),
    path('trailers/', trailers, name='trailers'),
    path('pos/', pos, name='pos'),
    path('pos/select_driver/<int:txTypeId', select_driver, name='select_driver'),
    path('pos/inv_req/<int:txId>/', inv_req, name='inv_req'),
    path('pos/inv_req/<int:txId>/<int:partId>/', inv_req_delete, name='inv_req_delete'),
    path('pos/inv_exp/<int:txId>', inv_exp, name='inv_exp'),
    path('drivers/', drivers, name='drivers'),
    path('reports/', reports, name='reports'),
    path('reports/monthlydriver', monthly_driver, name='monthly_driver'),
    path('reports/weeklydriver', weekly_driver, name='weekly_driver'),
    path('reports/rollingparts', rolling_parts, name='rolling_parts'),
    path('print_barcodes', print_barcodes, name='print_barcodes'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activate, name='activate')
]

"""
 path('api/orders/current/', current_order, name='api_current_order'),
 path('api/orders/current/items/', current_order_items, name='api_current_order_items'),
 path('api/orders/current/items/<item_id>/', current_order_item, name='api_product'),
 """