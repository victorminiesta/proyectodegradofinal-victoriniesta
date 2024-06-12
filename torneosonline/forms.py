from django import forms
from .models import Usuario, Videojuego
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms.widgets import ClearableFileInput
        
class RegistroUsuarios(UserCreationForm):
    username = forms.CharField(label="Nombre de Usuario", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Correo Electrónico", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Contraseña ",widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Repite la Contraseña",widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Usuario
        fields = ["username", "email", "password1", "password2"]
        
        
class EditarUsuario(UserChangeForm):
    username = forms.CharField(label="Nombre de Usuario", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Correo Electrónico", widget=forms.TextInput(attrs={'class': 'form-control'}))
    nombre = forms.CharField(label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    apellidos = forms.CharField(label="Apellidos", widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    imagen = forms.ImageField(label="Imagen de Perfil", required=False)

    password = None

    class Meta:
        model = Usuario
        fields = ["email", "username", "nombre", "apellidos", "imagen"]
        
class formCrearUsuariosAdministrador(UserCreationForm):
    username = forms.CharField(label="Nombre de Usuario", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Correo Electrónico", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Contraseña ",widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Repita la Contraseña",widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    admin = forms.BooleanField(required=False, label='Administrador')
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 'admin']
        
    
    # Uso la función save para personanilzar cómo se va a guardar el formulario en la base de datos (Django proporciona una implementación básica para crear usuarios)
    # necesito personalizarla debido que necesito manejar los campos de email y admin.    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = self.cleaned_data.get('admin', False)
        if commit:
            user.save()
        return user
    
    
    
class formEditarUsuarioAdministracion(UserChangeForm):
    username = forms.CharField(label="Nombre de Usuario", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Correo Electrónico", widget=forms.TextInput(attrs={'class': 'form-control'}))
    nombre = forms.CharField(label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    apellidos = forms.CharField(label="Apellidos", widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    imagen = forms.ImageField(label="Imagen de Perfil", required=False )
    admin = forms.BooleanField(required=False, label='Administrador', widget=forms.CheckboxInput(attrs={'class': 'btn btn-outline-primary'}))

    password = None

    class Meta:
        model = Usuario
        fields = ["admin", "email", "username", "nombre", "apellidos", "imagen"]
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_staff = self.cleaned_data.get('admin', False)
        if commit:
            user.save()
        return user