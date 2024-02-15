
from django.contrib import admin
from django.urls import path , include

from django.conf.urls.static import static
from django.conf import settings
from store import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
]