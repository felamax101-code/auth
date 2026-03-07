from django.urls import path
from . import views 
urlpatterns=[
    path("categories/",views.CategoryView.as_view()),
    path("products/",views.ProductView.as_view()),
    path("products/<int:pk>/",views.ProductDetailView.as_view()),
    path("cart/",views.CartView.as_view()),
    path("cart/add/",views.CartItemView.as_view()),
    path("cart/remove/<int:pk>/",views.CartItemView.as_view()),
    path("orders/",views.OrderView.as_view()),
    path("orders/checkout/",views.CheckoutView.as_view()),
    path("orders/<int:pk>/",views.OrderDetailView.as_view())
       
]