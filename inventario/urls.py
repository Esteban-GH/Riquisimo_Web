from django.urls import path
from .views import (
    stock_admin, 
    mermas_publico, 
    registrar_admin,
    generar_reporte_mermas_pdf,
    MermasPublicoView,
    detalle_merma,
    search_products
)

urlpatterns = [
    path('admin/', stock_admin, name='stock_admin'),
    path('search/', search_products, name='search_products'),
    path('detalle-merma/<int:merma_id>/', detalle_merma, name='detalle_merma'),
    path('mermas/', MermasPublicoView.as_view(), name='mermas_publico'),
    path('mermas/reporte-pdf/', generar_reporte_mermas_pdf, name='reporte_mermas_pdf'),
    path('registrar-admin/', registrar_admin, name='registrar_admin'),
]