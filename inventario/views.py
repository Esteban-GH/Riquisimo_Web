from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth import logout
from .models import Producto, Merma
from .forms import ProductoForm
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from .forms import AdminUserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AdminUserCreationForm

def stock_publico(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'inventario/stock_publico.html', {
        'productos': productos
    })

class CustomLoginView(LoginView):
    template_name = 'ingreso/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        messages.success(self.request, '¡Bienvenido al sistema Riquísimo!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error: Usuario o contraseña incorrectos')
        return super().form_invalid(form)

def custom_logout(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('stock_publico')

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
                        'fecha_actualizacion': producto.fecha_actualizacion.strftime("%d/%m/%Y %H:%M"),
                    }
                })
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        elif operation == 'update':
            producto_id = request.POST.get('id')
            producto = get_object_or_404(Producto, pk=producto_id)
            form = ProductoForm(request.POST, instance=producto)
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
                        'fecha_actualizacion': producto.fecha_actualizacion.strftime("%d/%m/%Y %H:%M"),
                    }
                })
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

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
                return JsonResponse({'success': False, 'errors': {'cantidad': 'Cantidad inválida'}}, status=400)

            if cantidad > producto.cantidad:
                return JsonResponse({'success': False, 'errors': {'cantidad': 'No hay suficiente stock'}}, status=400)

            merma = Merma(producto=producto, cantidad=cantidad, motivo=motivo, usuario=request.user)

            try:
                merma.full_clean()
                merma.save()
                producto.cantidad -= cantidad  # Actualizar stock directamente
                producto.save()
            except ValidationError as e:
                return JsonResponse({'success': False, 'errors': e.message_dict}, status=400)

            messages.success(request, 'Merma registrada exitosamente')
            return redirect('inventario:mermas_publico')  # Usar namespace correcto

    # Si GET u otro método
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'inventario/stock_admin.html', {
        'productos': productos,
        'unidades': dict(Producto.UNIDADES)
    })

def mermas_publico(request):
    mermas = Merma.objects.select_related('producto', 'usuario').order_by('-fecha_registro')
    return render(request, 'inventario/mermas_publico.html', {  # Asegúrate de que esta plantilla exista
        'mermas': mermas
    })

@login_required
def detalle_merma(request, merma_id):
    merma = get_object_or_404(Merma, pk=merma_id)
    return render(request, 'pantalla_merma/merma.html', {
        'merma': merma
    })





def registrar_admin(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Usuario registrado y logueado exitosamente.')
                return redirect('inventario:stock_admin')
            else:
                messages.error(request, 'Error al iniciar sesión después del registro.')

    else:
        form = AdminUserCreationForm()
    return render(request, 'ingreso/registrar_admin.html', {'form': form})