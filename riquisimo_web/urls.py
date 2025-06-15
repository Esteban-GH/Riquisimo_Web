from django.contrib import admin
from django.urls import path, include
from inventario.views import CustomLoginView, custom_logout, stock_publico

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', stock_publico, name='stock_publico'),
    path('inventario/', include('inventario.urls')),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', custom_logout, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
]