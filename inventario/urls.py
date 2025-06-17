from django.urls import path
from .views import stock_admin, mermas_publico, mermas_publico,registrar_admin
from . import views

urlpatterns = [
    path('admin/', views.stock_admin, name='stock_admin'),
    path('search/', views.search_products, name='search_products'),
    path('detalle-merma/<int:merma_id>/', views.detalle_merma, name='detalle_merma'),
    path('mermas/', views.mermas_publico, name='mermas_publico'),
   path('registrar-admin/', views.registrar_admin, name='registrar_admin'),
]