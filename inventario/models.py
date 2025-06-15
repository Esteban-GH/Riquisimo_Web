from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Producto(models.Model):
    UNIDADES = [
        ('un', 'Unidades'),
        ('kg', 'Kilogramos'),
        ('lt', 'Litros'),
        ('lata', 'Latas'),
    ]
    
    nombre = models.CharField(max_length=100)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unidad = models.CharField(max_length=10, choices=UNIDADES)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.get_unidad_display()})"

class Merma(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    motivo = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def clean(self):
        # Validar que la cantidad no sea mayor que el stock actual
        if self.cantidad > self.producto.cantidad:
            raise ValidationError("No puede registrar una merma mayor al stock disponible")
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecuta las validaciones (incluyendo clean())
        
        # Actualizar el stock del producto
        nuevo_stock = self.producto.cantidad - self.cantidad
        if nuevo_stock < 0:
            raise ValidationError("Stock insuficiente para esta merma")
        self.producto.cantidad = nuevo_stock
        self.producto.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Merma de {self.cantidad} de {self.producto.nombre}"
