# Generated by Django 5.2.3 on 2025-06-18 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0005_remove_usuarios_cargo'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuarios',
            name='comunidad',
            field=models.CharField(default='', max_length=200, verbose_name='Comunidad'),
        ),
        migrations.AddField(
            model_name='usuarios',
            name='foto',
            field=models.FileField(default='', upload_to='fotos/', verbose_name='Imagen'),
        ),
        migrations.AddField(
            model_name='usuarios',
            name='jefe_calle',
            field=models.BooleanField(default=False),
        ),
    ]
