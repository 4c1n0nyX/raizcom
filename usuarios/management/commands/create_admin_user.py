from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from getpass import getpass

class Command(BaseCommand):
    help = 'Crea un nuevo superusuario y lo asigna al grupo "administrador".'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            help='Nombre de usuario para el nuevo superusuario administrador.',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='',
            help='Email del usuario (opcional).',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        email = options['email']

        self.stdout.write(self.style.NOTICE(
            f"Por favor, introduce la contraseña para el usuario '{username}'."
        ))
        while True:
            password = self._get_input_password()
            if not password:
                self.stderr.write(self.style.ERROR("La contraseña no puede estar vacía."))
                continue
            password_confirm = self._get_input_password(confirm=True)
            if password == password_confirm:
                break
            else:
                self.stderr.write(self.style.ERROR("Las contraseñas no coinciden. Inténtalo de nuevo."))

        self.stdout.write(self.style.SUCCESS(f"Intentando crear/actualizar el usuario '{username}'..."))

        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_staff': True,
                    'is_superuser': True,
                }
            )

            user.set_password(password)
            user.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f"Superusuario '{username}' creado exitosamente."))
            else:
                self.stdout.write(self.style.SUCCESS(f"Contraseña y atributos de superusuario para '{username}' actualizados exitosamente."))

            try:
                admin_group, group_created = Group.objects.get_or_create(name='administrador')
                if group_created:
                    self.stdout.write(self.style.SUCCESS("Grupo 'administrador' creado automáticamente."))

                if admin_group not in user.groups.all():
                    user.groups.add(admin_group)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"Usuario '{username}' añadido al grupo 'administrador'."))
                else:
                    self.stdout.write(self.style.WARNING(f"Usuario '{username}' ya es miembro del grupo 'administrador'."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al asignar usuario al grupo 'administrador': {e}"))
                self.stdout.write(self.style.WARNING(
                    "ADVERTENCIA: Asegúrate de que el grupo 'administrador' existe en tu base de datos "
                    "y que tienes los permisos adecuados."
                ))

            self.stdout.write(self.style.SUCCESS(f"Operación para el usuario '{username}' completada."))

        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"Error en el comando: {e}"))
        except Exception as e:
            raise CommandError(f"Error inesperado al procesar el usuario '{username}': {e}")

    def _get_input_password(self, confirm=False):
        """Helper para pedir la contraseña de forma segura."""
        prompt = "Contraseña: "
        if confirm:
            prompt = "Confirma la contraseña: "

        return getpass(prompt)
