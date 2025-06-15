from django.urls import path
from .views import stock_admin

urlpatterns = [
    path('admin/', stock_admin, name='stock_admin'),
]