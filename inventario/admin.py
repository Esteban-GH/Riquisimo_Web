from django.contrib import admin
from .models import Producto, Merma

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad', 'unidad', 'fecha_actualizacion')
    list_filter = ('unidad',)
    search_fields = ('nombre',)

class MermaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad', 'fecha_registro', 'usuario')
    list_filter = ('fecha_registro', 'usuario')
    readonly_fields = ('fecha_registro',)

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Merma, MermaAdmin)