from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm, RegisterForm

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart, name='cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=LoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('vnpay-return/', views.vnpay_return, name='vnpay_return'),
]