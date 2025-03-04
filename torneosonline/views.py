from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from .models import Videojuego, Usuario, Torneo, Partida, Amonestacion, Logro, Historial
from django.views import View
from django.urls import reverse_lazy
from django.urls import reverse
from typing import Any
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView, ListView
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.forms import BaseModelForm, DateTimeInput, TextInput, NumberInput
from .forms import RegistroUsuarios, EditarUsuario, formCrearUsuariosAdministrador, formEditarUsuarioAdministracion
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from urllib.parse import urlencode
from django.contrib.auth.forms import SetPasswordForm
import os
import shutil
import random
from django.conf import settings
from django.contrib import messages
from django.utils import timezone


# Create your views here.


'''
Pantalla de bienvenida con botón de entrar:

Si hay información importante que deseas comunicar a los usuarios antes de que accedan al sitio principal (como reglas del torneo, premios, consejos para inscribirse, etc.),
una pantalla de bienvenida con un botón de entrar podría ser útil.
Esta opción te brinda la oportunidad de orientar a los usuarios sobre cómo utilizar la aplicación,
qué pueden esperar de los torneos y cualquier otra información relevante que desees destacar.

'''


def Bienvenida(request):
    template_name="torneosonline/Bienvenida.html"
    return render(request, template_name)

@staff_member_required
def Administracion(request):
    template_name = "torneosonline/administracion/Administracion.html"
    return render(request, template_name)

class Perfil(LoginRequiredMixin, ListView):
    model = Usuario
    template_name = 'registration/perfil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        context['usuario'] = usuario
        amonestaciones = Amonestacion.objects.filter(usuario=usuario)
        context['numeroAmonestaciones'] = amonestaciones.count()
        return context

class EditarPerfil(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = EditarUsuario
    template_name = 'registration/editarPerfil.html'
    success_url = reverse_lazy("Videojuegos")
    
    def form_valid(self, form):
        # Obtener la instancia del usuario
        usuario = form.instance        
        carpeta = settings.MEDIA_ROOT+"perfiles/"+usuario.username
        
        if not usuario.imagen:
            usuario.imagen = "perfiles/default_img_profile"
        else:
            if 'imagen' in form.changed_data:
                try:
                    for imagen in os.listdir(carpeta):
                        ruta_completa = os.path.join(carpeta, imagen)
                        if (imagen != usuario.imagen):
                            os.remove(ruta_completa)
                except FileNotFoundError:
                    messages.error(self.request, "No se ha encontrado la imagen.") 
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        # Construir la URL de redirección con el mensaje de éxito
        mensaje_URL = urlencode({'success_message': "Perfil actualizado correctamente."})
        # Creo una url de redirección con el mensaje
        return "{}?{}".format(super().get_success_url(), mensaje_URL)
    
def EditarContrasena(request):
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Vuelvo a iniciar sesion debido a que al cambiar la contraseña se cierra sesión automáticamente
            login(request, request.user)
            return redirect('Perfil')
    else:
        form = SetPasswordForm(request.user)
    return render(request, 'registration/editarContrasena.html', {'form': form})
    

class CrearTorneos(CreateView):
    model = Torneo
    fields = "__all__"
    template_name = "torneosonline/administracion/torneos/CrearTorneo.html"
    
    # Por alguna razón que desconozco todavía, django me crea en el formulario el campo de datetime como si fuese un varchar en vez de un datetime 
    # asi que sobrescribo el método 'get_form()' de la CreateView editando el campo de fecha y establezco su widget como 'DateTimeInput'
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['nombre'].widget = TextInput(attrs={'class': 'form-control'})
        form.fields['fecha'].widget = DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        form.fields['numerojugadores'].widget = NumberInput(attrs={'class': 'form-control'})
        return form
    
    success_url = reverse_lazy("AdministrarTorneos")
    
class CrearTorneosUsuarios(LoginRequiredMixin, CreateView):
    model = Torneo
    fields=["nombre", "fecha", "numerojugadores"]
    template_name = "torneosonline/administracion/torneos/CrearTorneoUsuarios.html"
    success_url = reverse_lazy("Videojuegos")
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['nombre'].widget = TextInput(attrs={'class': 'form-control'})
        form.fields['fecha'].widget = DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        form.fields['numerojugadores'].widget = NumberInput(attrs={'class': 'form-control'})
        return form
        
    def get_queryset(self):
        nombre = self.kwargs.get('nombreVideojuego')
        nombre = nombre.replace('-', ' ')
        videojuego = Videojuego.objects.get(nombre=nombre)  # Obtener el objeto videojuego
        return videojuego
    
    def form_valid(self, form):
        fechaActual = timezone.now()
        fechaTorneo = form.cleaned_data.get('fecha')
        una_hora_desde_hoy = fechaActual + timezone.timedelta(hours=1)
        
        if fechaTorneo < una_hora_desde_hoy:
            form.add_error('fecha', 'La fecha del torneo debe ser al menos una hora después.')
            return self.form_invalid(form)
        
        inscribirsePropio = self.request.POST.get('inscribirsePropio')
        torneo = form.save(commit=False)
        usuario = self.request.user 
        
        if inscribirsePropio:  
            torneo.videojuego = self.get_queryset()
            torneo.creador = usuario
            torneo.save()
            torneo.usuarios.add(usuario)
        else:
            torneo.videojuego = self.get_queryset()
            torneo.creador = usuario
            torneo.save()
        return super().form_valid(form)
    
     
def EliminarTorneos(request, pk):
    if request.method == "DELETE":
        torneo = get_object_or_404(Torneo, pk=pk)
        torneo.delete()
        # Devuelvo una respuesta HTTP con un código de estado 200(ok) por defecto que indica que la solicitud tuvo exito.
        # No necesito hace un return (render) o similar debido a que al hacer la solicitud ajax no necesito redirigir al usuario a una nueva página. 
        return HttpResponse()
    
class EditarTorneos(UpdateView):
    model = Torneo
    fields = "__all__"
    template_name = "torneosonline/administracion/torneos/EditarTorneo.html"
    success_url = reverse_lazy("AdministrarTorneos")
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['fecha'].widget = DateTimeInput(attrs={'type': 'datetime-local'})
        return form
    
class CrearAmonestacion(CreateView):
    model = Amonestacion
    template_name = "torneosonline/administracion/usuarios/CrearAmonestacion.html"
    fields = "__all__"
    success_url = reverse_lazy("AdministrarUsuarios")
    
class Amonestaciones(ListView):
    model =  Amonestacion
    template_name = 'torneosonline/administracion/usuarios/Amonestaciones.html'
    context_object_name = 'amonestaciones'
    
class AdministrarTorneos(ListView):
    model = Torneo
    template_name = "torneosonline/administracion/torneos/AdministracionTorneos.html"
    context_object_name = "torneos"
    
class DetallesTorneoAdministracion(DetailView):
    model = Torneo
    template_name = "torneosonline/administracion/torneos/DetallesTorneo.html"
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["usuarios"] = self.object.usuarios.all()
        return context
    
def register(request):
    if request.method == "POST":
        form = RegistroUsuarios(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("Videojuegos")
    else:
        form = RegistroUsuarios()
        
    return render(request, "registration/registro.html", {"form":form})
     

class Videojuegos(ListView):
    model = Videojuego
    template_name = "torneosonline/Videojuegos.html"
    context_object_name = "videojuegos"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        success_message = self.request.GET.get('success_message')
        if success_message:
            context['success_message'] = success_message
        return context
    
class Torneos(ListView):
    model = Torneo
    template_name = "torneosonline/Torneos.html"
    context_object_name = "torneos"
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["fechaActual"] = timezone.now()
        return context
    
    # Uso el metodo get_queryset para recuperar el objecto videojuego__nombre filtrado por el nombre pasado desde la url
    
    def get_queryset(self):
        nombre = self.kwargs.get('nombreVideojuego')
        nombre = nombre.replace('-', ' ')
        queryset = Torneo.objects.filter(videojuego__nombre = nombre)
        return queryset   
    
class DetallesTorneos(DetailView):
    model = Torneo
    template_name = "torneosonline/DetallesTorneo.html"
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        torneo = self.object
        context["usuarios"] = torneo.usuarios.all()
        context["fechaActual"] = timezone.now()
        
        try:
            partida = Partida.objects.get(torneo=torneo)
            context["partida"] = partida
        except Partida.DoesNotExist:
            context["partida"] = None
        return context
class AdministrarVideojuegos(ListView):
    model = Videojuego
    template_name = "torneosonline/administracion/videojuegos/AdministracionVideojuegos.html"
    context_object_name = "videojuegos"
    
class CrearVideojuego(CreateView):
    model = Videojuego
    fields = "__all__"
    template_name = "torneosonline/administracion/videojuegos/CrearVideojuego.html"
    success_url = reverse_lazy("AdministrarVideojuegos")
    
class EditarVideojuego(UpdateView):
    model = Videojuego
    fields = "__all__"
    template_name = "torneosonline/administracion/videojuegos/EditarVideojuego.html"
    success_url = reverse_lazy("AdministrarVideojuegos")
    
    def form_valid(self, form):
        # Obtener la instancia del videojuego
        videojuego = form.instance        
        carpeta = settings.MEDIA_ROOT+"videojuegos/"+videojuego.nombre
        
        if 'imagen' in form.changed_data:
            try:
                for imagen in os.listdir(carpeta):
                    ruta_completa = os.path.join(carpeta, imagen)
                    if (imagen != videojuego.imagen):
                        os.remove(ruta_completa)
            except FileNotFoundError:
                messages.error(self.request, "No se ha encontrado la imagen.") 
        response = super().form_valid(form)
        return response
    
def EliminarVideojuegos(request, pk):
    if request.method == "DELETE":
        videojuego = get_object_or_404(Videojuego, pk=pk)
        Torneo.objects.filter(videojuego=videojuego).delete()
        videojuego.delete()
        carpeta = settings.MEDIA_ROOT+"perfiles/"+videojuego
        os.remove(carpeta)
        # Devuelvo una respuesta HTTP con un código de estado 200(ok) por defecto que indica que la solicitud tuvo exito.
        # No necesito hace un return (render) o similar debido a que al hacer la solicitud ajax no necesito redirigir al usuario a una nueva página. 
        return HttpResponse()
    
    
class AdministrarUsuarios(ListView):
    model = Usuario
    template_name = "torneosonline/administracion/usuarios/AdministracionUsuarios.html"
    context_object_name = "usuarios"
    
class CrearUsuarioAdministracion(CreateView):
    model = Usuario
    template_name = "torneosonline/administracion/usuarios/CrearUsuario.html"
    form_class = formCrearUsuariosAdministrador
    success_url = reverse_lazy('AdministrarUsuarios')
    
    def form_valid(self, form):
        print(form)
        form.save()
        return super().form_valid(form)
    
class EditarUsuarioAdministracion(UpdateView):
    model = Usuario
    template_name = "torneosonline/administracion/usuarios/EditarUsuario.html"
    form_class = formEditarUsuarioAdministracion
    success_url = reverse_lazy('AdministrarUsuarios')
    
    def form_valid(self, form):
        # Obtener la instancia del usuario
        usuario = form.save(commit=False)        
        carpeta = settings.MEDIA_ROOT+"perfiles/"+usuario.username

        if not usuario.imagen:
            usuario.imagen = "perfiles/default_img_profile"
        else:
            if 'imagen' in form.changed_data:
                try:
                    for imagen in os.listdir(carpeta):
                        ruta_completa = os.path.join(carpeta, imagen)
                        if (imagen != usuario.imagen):
                            os.remove(ruta_completa)
                except FileNotFoundError:
                    messages.error(self.request, "No se ha encontrado la imagen.") 
        response = super().form_valid(form)
        return response
    
@staff_member_required
def EliminarUsuario(request, pk):
    if request.method == "DELETE":
        usuario = get_object_or_404(Usuario, pk=pk)

        # Ruta de la carpeta del usuario
        carpeta = os.path.join(settings.MEDIA_ROOT, "perfiles", usuario.username)

        # Verificar si la carpeta existe antes de eliminarla
        if os.path.exists(carpeta):
            try:
                shutil.rmtree(carpeta)  # Eliminar la carpeta y su contenido
            except PermissionError:
                return JsonResponse({"error": "No se pudo eliminar la carpeta del usuario."}, status=500)

        usuario.delete()  # Eliminar el usuario de la base de datos
        return JsonResponse({"mensaje": "Usuario eliminado correctamente."}, status=200)

    return JsonResponse({"error": "Método no permitido."}, status=405)


def inscribirseTorneo(request, pk):
        if not request.user.is_authenticated:
            return HttpResponseBadRequest("Usted no está logueado.")
    
        try:
            torneo = get_object_or_404(Torneo, pk=pk)
            usuario = request.user
            torneo.usuarios.add(usuario)
            return HttpResponse()
        except Torneo.DoesNotExist:
            return HttpResponseBadRequest("El torneo no existe.")

def desinscribirseTorneo(request, pk):
    torneo = get_object_or_404(Torneo, pk=pk)
    usuario = request.user
    torneo.usuarios.remove(usuario)
    return HttpResponse()


def crearPartida(request, pk):
    if request.method == "POST":
        torneo = get_object_or_404(Torneo, id=pk)
        
        if not Partida.objects.filter(torneo=torneo).exists():
            usuarios = torneo.usuarios.all()
            
            if usuarios.count() >= 2:
                ganador = random.choice(usuarios)
                nuevaPartida = Partida.objects.create(torneo=torneo, ganador=ganador)
                nuevaPartida.save()
                return HttpResponse()
            else:
                return HttpResponseBadRequest("No hay suficiusuarios inscritos en el torneo.")
            
class AdministrarPartidas(ListView):
    model = Partida
    template_name = "torneosonline/administracion/partidas/AdministracionPartidas.html"
    context_object_name = "partidas"
    
class EditarPartida(UpdateView):
    model = Partida
    template_name = "torneosonline/administracion/partidas/EditarPartida.html"
    fields = "__all__"
    success_url = reverse_lazy('AdministrarPartidas')
    
def EliminarPartida(request, pk):
    if request.method == "DELETE":
        partida = get_object_or_404(Partida, pk=pk)
        partida.delete() 
        return HttpResponse()