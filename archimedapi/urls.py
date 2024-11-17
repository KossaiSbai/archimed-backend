"""
URL configuration for archimedapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from archimedapi.views import (
    bill_investor,
    bill_detail,
    bill_list,
    capital_call_detail,
    capital_call_list,
    index,
    investment_list,
    investment_detail,
    entity_list,
    entity_detail
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name='index'),
    path("capital_calls/", capital_call_list, name='capital-call-list'),
    path('capital_calls/<str:pk>/', capital_call_detail, name='capital-call-detail'),
    path("bills/", bill_list, name='bill-list'),
    path("bills/<str:pk>/", bill_detail, name='bill-detail'),
    path("create_bill/", bill_investor, name='bill-investor'),
    path("entities/", entity_list, name='entity-list'),
    path("entities/<str:pk>/", entity_detail, name='entity-detail'),
    path("investments/", investment_list, name='investment-list'),
    path("investments/<str:pk>/", investment_detail, name='investment-detail'),
]
