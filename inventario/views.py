from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth import logout
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from .models import Producto, Merma
from .forms import ProductoForm

def stock_publico(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'inventario/stock_publico.html', {
        'productos': productos
    })

@login_required
@require_http_methods(["GET", "POST"])
def stock_admin(request):
    if request.method == 'POST':
        operation = request.POST.get('operation')

        if operation == 'create':
            form = ProductoForm(request.POST)
            if form.is_valid():
                producto = form.save()
                return JsonResponse({
                    'success': True,
                    'producto': {
                        'id': producto.id,
                        'nombre': producto.nombre,
                        'cantidad': float(producto.cantidad),
                        'unidad': producto.unidad,
                        'unidad_display': producto.get_unidad_display(),
                    }
                })
            return JsonResponse({'success': False, 'error': form.errors}, status=400)

        elif operation == 'delete':
            producto_id = request.POST.get('id')
            producto = get_object_or_404(Producto, pk=producto_id)
            producto.delete()
            return JsonResponse({'success': True})

        elif operation == 'merma':
            producto_id = request.POST.get('producto_id')
            cantidad = request.POST.get('cantidad')
            motivo = request.POST.get('motivo')

            producto = get_object_or_404(Producto, pk=producto_id)

            try:
                cantidad = Decimal(cantidad)
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, InvalidOperation):
                return JsonResponse({'success': False, 'error': {'cantidad': 'Cantidad inválida'}}, status=400)

            if cantidad > producto.cantidad:
                return JsonResponse({'success': False, 'error': {'cantidad': 'No hay suficiente stock'}}, status=400)

            merma = Merma(
                producto=producto, 
                cantidad=cantidad, 
                motivo=motivo, 
                usuario=request.user
            )

            try:
                merma.full_clean()
                merma.save()
                
                # Actualizar stock del producto
                producto.cantidad -= cantidad
                producto.save()
                
                return JsonResponse({
                    'success': True,
                    'producto_id': producto.id,
                    'producto_nombre': producto.nombre,
                    'nuevo_stock': float(producto.cantidad)
                })
            except ValidationError as e:
                return JsonResponse({'success': False, 'error': e.message_dict}, status=400)

        elif operation == 'agregar_stock':
            producto_id = request.POST.get('producto_id')
            cantidad = request.POST.get('cantidad')

            producto = get_object_or_404(Producto, pk=producto_id)

            try:
                cantidad = Decimal(cantidad)
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, InvalidOperation):
                return JsonResponse({'success': False, 'error': 'Cantidad inválida'}, status=400)

            producto.cantidad += cantidad
            producto.save()

            return JsonResponse({
                'success': True,
                'producto_id': producto.id,
                'producto_nombre': producto.nombre,
                'nuevo_stock': float(producto.cantidad)
            })

        elif operation == 'quitar_stock':
            producto_id = request.POST.get('producto_id')
            cantidad = request.POST.get('cantidad')

            producto = get_object_or_404(Producto, pk=producto_id)

            try:
                cantidad = Decimal(cantidad)
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, InvalidOperation):
                return JsonResponse({'success': False, 'error': 'Cantidad inválida'}, status=400)

            if cantidad > producto.cantidad:
                return JsonResponse({'success': False, 'error': 'No hay suficiente stock'}, status=400)

            producto.cantidad -= cantidad
            producto.save()

            return JsonResponse({
                'success': True,
                'producto_id': producto.id,
                'producto_nombre': producto.nombre,
                'nuevo_stock': float(producto.cantidad)
            })

    # GET request
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'inventario/stock_admin.html', {
        'productos': productos,
        'unidades': dict(Producto.UNIDADES)
    })

def custom_logout(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('stock_publico')

class CustomLoginView(LoginView):
    template_name = 'ingreso/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        messages.success(self.request, '¡Bienvenido al sistema Riquísimo!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error: Usuario o contraseña incorrectos')
        return super().form_invalid(form)