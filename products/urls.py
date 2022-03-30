from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('product/<str:pid>', views.product, name='products'),
    path('cart/', views.cart, name='cart'),
    path('calculation/', views.calculation, name='calculation'),
    path('thankyou/', views.thankyou, name='thankyou'),
    path('user', views.user, name='user'),
    path('payment/<str:val>', views.payment, name='payment'),
    path('paymentgateway', views.paymentgateway, name='paymentgateway'),
]