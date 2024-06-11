import random
from django.utils import timezone
from .models import Torneo, Partida

def crearPartida():
    ahora = timezone.now()
    torneos = Torneo.objects.filter(fecha__lte=ahora, fecha__gt=ahora - timezone.timedelta(minutes=1))

    for torneo in torneos:
        partida_existente = Partida.objects.filter(torneo=torneo).exists()
        
        if not partida_existente:
            usuarios_inscritos = torneo.usuarios.all()

            if usuarios_inscritos:
                ganador = random.choice(usuarios_inscritos)
                nueva_partida = Partida.objects.create(torneo=torneo, ganador=ganador)
                nueva_partida.save()