from django import forms
from .models import Producto
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'cantidad', 'unidad']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'unidad': forms.Select(attrs={'class': 'form-control'}),
        }

class AdminUserCreationForm(UserCreationForm):
    is_staff = forms.BooleanField(label='Es administrador', required=False, initial=True,
                                  help_text='Marque esta casilla si el usuario debe tener permisos de administrador.')






    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'is_staff')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        # Aquí siempre lo marcas como admin
        user.is_staff = True
        if commit:
            user.save()
        return user
    