import time
import asyncio
from django.core.management.base import BaseCommand
from chat.emergencies import enviar_alertas # O el nombre de tu archivo si es diferente

class Command(BaseCommand):
    help = 'Ejecuta el bot de alertas de sismos y otras alertas para la aplicación web.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Iniciando bot de alertas multi-tipo para la web..."))
        loop = asyncio.get_event_loop()
        while True:
            self.stdout.write("Verificando nuevas alertas (sismos, meteorológicas, etc.)...")
            loop.run_until_complete(enviar_alertas())
            self.stdout.write("Esperando 2 minutos antes de la próxima verificación...")
            time.sleep(120)