from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Videojuego(models.Model):
    
    def directorioImgVideojuegos(instance, filename):
        nombre = instance.nombre
        return os.path.join('videojuegos', nombre, filename)
    
    nombre = models.CharField('Nombre', max_length=100, unique = True)
    imagen = models.ImageField("Imagen del Videojuego", upload_to=directorioImgVideojuegos, height_field=None, width_field=None)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Videojuegos"

class Usuario(AbstractUser):
    
    # Determinar la ubicación donde se almacenarán las imágenes de perfil de los usuarios en función de su nombre de usuario.
    
    def directorioImgPerfiles(instance, filename):
        username = instance.username
        return os.path.join('perfiles', username, filename)
    
    username = models.CharField('Nombre de Usuario', unique = True, max_length=20)
    email = models.EmailField('Correo Electrónico', max_length=250, unique = True)
    nombre = models.CharField('Nombre', max_length=200, blank = True, null = True)
    apellidos = models.CharField('Apellidos', max_length=50, blank = True, null = True)
    imagen = models.ImageField('Imagen de Perfil', upload_to=directorioImgPerfiles, height_field=None, width_field=None, default='perfiles/default_img_profile.jpg')
    
    def __str__(self):
        return f'{self.username}'
    
    class Meta:
        verbose_name_plural = "Usuarios"
    
class Torneo(models.Model):
    nombre = models.CharField('Nombre', max_length=24)
    fecha = models.DateTimeField('Fecha', null = True)
    numerojugadores = models.IntegerField('Número de Jugadores', validators=[MinValueValidator(2)])
    usuarios = models.ManyToManyField(Usuario, blank=True)
    videojuego = models.ForeignKey(Videojuego, on_delete=models.CASCADE)
    # Necesito establecerle un related name debido a que sino da un conflicto ambas claves foraneas
    creador = models.ForeignKey(Usuario, null = True, blank= True, on_delete=models.CASCADE, related_name='creador')
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Torneos"

class Partida(models.Model):    
    ganador = models.ForeignKey(Usuario, on_delete=models.CASCADE, max_length=50, null = True, blank= True)
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'Partida del torneo {self.torneo}'
    
    class Meta:
        verbose_name_plural = "Partidas"
    
class Amonestacion(models.Model):
   usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
   descripcion = models.TextField()
   
   def __str__(self):
       return f'Id de amonestación: {self.pk}, usuario: {self.usuario}'
    

   class Meta:
        verbose_name_plural = "Amonestaciones"


class Logro(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    imagen = models.ImageField('Imagen del logro', upload_to='logros/', height_field=None, width_field=None)
    
    def __str__(self):
        return f'Logro {self.nombre}'
    
    class Meta:
        verbose_name_plural = "Logros"
    
class Historial(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    torneos = models.ManyToManyField(Torneo, blank=True)
    
    def __str__(self):
        return f'Historial de {self.usuario}'
    
    class Meta:
        verbose_name_plural = "Historiales"