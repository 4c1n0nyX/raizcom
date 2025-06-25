from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Crea los grupos iniciales: administrador, publicador y estandar, y les asigna todos los permisos disponibles.'

    def handle(self, *args, **options):
        groups_to_process = ['administrador', 'publicador', 'estandar']
        
        self.stdout.write(self.style.SUCCESS("Iniciando creación de grupos y asignación de permisos..."))

        all_permissions = Permission.objects.all()
        
        if not all_permissions.exists():
            self.stdout.write(self.style.WARNING(
                "ADVERTENCIA: No se encontraron permisos en la base de datos. "
                "Asegúrate de haber ejecutado 'python manage.py migrate' para generar los permisos de tus modelos."
            ))
            return

        for group_name in groups_to_process:
            try:
                group, created = Group.objects.get_or_create(name=group_name)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Grupo '{group_name}' creado exitosamente."))
                else:
                    self.stdout.write(self.style.WARNING(f"Grupo '{group_name}' ya existe."))

                group.permissions.set(all_permissions)
                
                self.stdout.write(self.style.SUCCESS(f"  Todos los {all_permissions.count()} permisos disponibles asignados a '{group_name}'."))
                
                group.save()
                
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error al procesar el grupo '{group_name}': {e}"))
        
        self.stdout.write(self.style.SUCCESS("Proceso de creación de grupos y asignación de todos los permisos finalizado."))
