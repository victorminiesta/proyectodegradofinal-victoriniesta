from django.contrib import admin
from .models import Videojuego, Usuario, Torneo, Partida, Amonestacion, Logro, Historial
from django.contrib.auth.admin import UserAdmin

# Register your models here.

admin.site.register(Usuario, UserAdmin)
admin.site.register(Videojuego)
admin.site.register(Torneo)
admin.site.register(Partida)
admin.site.register(Amonestacion)
admin.site.register(Logro)
admin.site.register(Historial)





