from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Producto(models.Model):
    UNIDADES = [
        ('un', 'Unidades'),
        ('kg', 'Kilogramos'),
        ('lt', 'Litros'),
        ('lata', 'Latas'),
    ]
    
    nombre = models.CharField(max_length=100)
    cantidad = models.IntegerField(validators=[MinValueValidator(0)])
    unidad = models.CharField(max_length=10, choices=UNIDADES)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.get_unidad_display()})"

class Merma(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    motivo = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def clean(self):
        if self.cantidad > self.producto.cantidad:
            raise ValidationError({
                'cantidad': f"No puede registrar una merma de {self.cantidad} porque el stock actual es solo {self.producto.cantidad}"
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecuta las validaciones (incluyendo clean)
        
        # Actualizar el stock del producto
        self.producto.cantidad -= self.cantidad
        self.producto.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Merma de {self.cantidad} de {self.producto.nombre}"