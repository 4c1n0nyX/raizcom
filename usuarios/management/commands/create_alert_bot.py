from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Crea o actualiza el usuario "alertas_bot" como superusuario.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            help='Contraseña para el usuario alertas_bot. Si no se proporciona, se buscará en la variable de entorno ALERTAS_BOT_PASSWORD.',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        password = options['password']
        
        if not password:
            password = os.environ.get('ALERTAS_BOT_PASSWORD') 

        if not password:
            raise CommandError(
                "La contraseña para 'alertas_bot' no se proporcionó. "
                "Usa --password=<tu_contraseña> o establece la variable de entorno ALERTAS_BOT_PASSWORD."
            )

        self.stdout.write(self.style.SUCCESS("Intentando crear/actualizar el usuario 'alertas_bot'..."))

        try:
            user, created = User.objects.get_or_create(
                username='alertas_bot',
                defaults={
                    'email': 'alertas_bot@example.com',
                    'first_name': 'Alertas',
                    'last_name': 'Bot',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )

            if created or options['password']:
                user.set_password(password)
                user.save()
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Usuario '{user.username}' creado exitosamente con la contraseña proporcionada/desde variable de entorno."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Contraseña del usuario '{user.username}' actualizada exitosamente."))
            else:
                needs_update = False
                if user.email != 'alertas_bot@example.com':
                    user.email = 'alertas_bot@example.com'
                    needs_update = True
                if user.first_name != 'Alertas':
                    user.first_name = 'Alertas'
                    needs_update = True
                if user.last_name != 'Bot':
                    user.last_name = 'Bot'
                    needs_update = True
                if not user.is_staff:
                    user.is_staff = True
                    needs_update = True
                if not user.is_superuser:
                    user.is_superuser = True
                    needs_update = True

                if needs_update:
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"Atributos del usuario '{user.username}' actualizados exitosamente (la contraseña existente se mantuvo)."))
                else:
                    self.stdout.write(self.style.WARNING(f"Usuario '{user.username}' ya existe y está actualizado. No se realizaron cambios."))

        except Exception as e:
            raise CommandError(f"Error al procesar el usuario 'alertas_bot': {e}")
