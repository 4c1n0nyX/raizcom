# Generated by Django 5.2.3 on 2025-06-19 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0009_remove_usuarios_apellido_remove_usuarios_correo_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuarios',
            name='tipo',
        ),
    ]
