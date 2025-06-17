from django.urls import path
from .views import stock_admin, detalle_merma, mermas_publico,registrar_admin

app_name = 'inventario'  # Añadir esta línea para soportar el namespace

urlpatterns = [
    path('admin/', stock_admin, name='stock_admin'),
    path('detalle-merma/<int:merma_id>/', detalle_merma, name='detalle_merma'),
    path('mermas/', mermas_publico, name='mermas_publico'),
    path('registrar-admin/', registrar_admin, name='registrar_admin'),
]
