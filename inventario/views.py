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
from django.views.generic import ListView 
from .reportes import generar_reporte_mermas
from datetime import datetime
from django.http import HttpResponse, JsonResponse 


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
                        'cantidad': producto.cantidad,
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
                cantidad = int(cantidad)
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': {'cantidad': 'Por favor, ingrese una cantidad válida (número entero mayor a 0).'}
                }, status=400)

            merma = Merma(
                producto=producto,
                cantidad=cantidad,
                motivo=motivo,
                usuario=request.user
            )

            try:
                merma.save()
                return JsonResponse({
                    'success': True,
                    'producto_id': producto.id,
                    'producto_nombre': producto.nombre,
                    'nuevo_stock': producto.cantidad
                })
            except ValidationError as e:
                return JsonResponse({
                    'success': False,
                    'error': {'cantidad': str(e) if not e.message_dict else e.message_dict.get('cantidad', 'Error al registrar merma')}
                }, status=400)

        elif operation == 'agregar_stock':
            producto_id = request.POST.get('producto_id')
            cantidad = request.POST.get('cantidad')

            producto = get_object_or_404(Producto, pk=producto_id)

            try:
                cantidad = int(cantidad)
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': {'cantidad': 'Por favor, ingrese una cantidad válida (número entero mayor a 0).'}
                }, status=400)

            producto.cantidad += cantidad
            producto.save()

            return JsonResponse({
                'success': True,
                'producto_id': producto.id,
                'producto_nombre': producto.nombre,
                'nuevo_stock': producto.cantidad
            })

        elif operation == 'quitar_stock':
            producto_id = request.POST.get('producto_id')
            cantidad = request.POST.get('cantidad')

            producto = get_object_or_404(Producto, pk=producto_id)

            try:
                cantidad = int(cantidad)
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': {'cantidad': 'Por favor, ingrese una cantidad válida (número entero mayor a 0).'}
                }, status=400)

            if cantidad > producto.cantidad:
                return JsonResponse({
                    'success': False,
                    'error': {'cantidad': f'No hay suficiente stock. Stock actual: {producto.cantidad}, intentaste quitar: {cantidad}'}
                }, status=400)

            producto.cantidad -= cantidad
            producto.save()

            return JsonResponse({
                'success': True,
                'producto_id': producto.id,
                'producto_nombre': producto.nombre,
                'nuevo_stock': producto.cantidad
            })

    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'inventario/stock_admin.html', {
        'productos': productos,
        'unidades': dict(Producto.UNIDADES)
    })

def search_products(request):
    if request.method == "GET":
        query = request.GET.get('q', '')
        if query:
            products = Producto.objects.filter(nombre__icontains=query)[:10]
            results = [
                {
                    'id': product.id,
                    'nombre': product.nombre,
                    'cantidad': product.cantidad,
                    'unidad_display': product.get_unidad_display()
                }
                for product in products
            ]
            return JsonResponse({'results': results})
        return JsonResponse({'results': []})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def stock_publico(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'inventario/stock_publico.html', {
        'productos': productos
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
    
def mermas_publico(request):
    mermas = Merma.objects.select_related('producto', 'usuario').order_by('-fecha_registro')
    return render(request, 'inventario/stock_publico', { 
        'mermas': mermas
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

@login_required
def mermas_publico(request):
    mermas = Merma.objects.select_related('producto', 'usuario').order_by('-fecha_registro')
    return render(request, 'inventario/mermas_publico.html', { 
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
        username = request.POST.get('username')
        password = request.POST.get('password1') 
        password2 = request.POST.get('password2')
        email = request.POST.get('email', '')

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'ingreso/registrar_admin.html', {
                'form': {'username': username, 'email': email}
            })

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'ingreso/registrar_admin.html', {
                'form': {'username': username, 'email': email}
            })

        try:
            user = User.objects.create_user(username=username, password=password, email=email, is_staff=True)
            login(request, user)
            messages.success(request, 'Usuario registrado y logueado exitosamente.')
            return redirect('inventario:stock_admin')
        except Exception as e:
            messages.error(request, f'Error al registrar el usuario: {str(e)}')
            return render(request, 'ingreso/registrar_admin.html', {
                'form': {'username': username, 'email': email}
            })

    return render(request, 'ingreso/registrar_admin.html', {'form': {}})

    
class MermasPublicoView(ListView):
    model = Merma
    template_name = 'inventario/mermas_publico.html'
    context_object_name = 'mermas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('producto', 'usuario')
        
        mes = self.request.GET.get('mes')
        año = self.request.GET.get('año')
        
        if mes and año:
            queryset = queryset.filter(
                fecha_registro__month=mes,
                fecha_registro__year=año
            )
        
        return queryset.order_by('-fecha_registro')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mes_actual'] = datetime.now().month
        context['año_actual'] = datetime.now().year
        return context

@login_required
def generar_reporte_mermas_pdf(request):
    mes = request.GET.get('mes', datetime.now().month)
    año = request.GET.get('año', datetime.now().year)
    
    mermas = Merma.objects.filter(
        fecha_registro__month=mes,
        fecha_registro__year=año
    ).select_related('producto', 'usuario')
    
    buffer = generar_reporte_mermas(mermas, mes, año)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_mermas_{mes}_{año}.pdf"'
    response.write(buffer.getvalue())
    buffer.close()
    
    return response
