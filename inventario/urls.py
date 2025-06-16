from django.urls import path
from .views import stock_admin
from . import views

urlpatterns = [
    path('admin/', stock_admin, name='stock_admin'),
    path('search/', views.search_products, name='search_products'),  # Nueva URL para búsqueda
]