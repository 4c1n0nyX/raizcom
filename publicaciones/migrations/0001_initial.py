# Generated by Django 5.2.3 on 2025-06-19 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Noticias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(default='', max_length=200, unique=True, verbose_name='Titulo')),
                ('contenido', models.CharField(default='', max_length=200, verbose_name='Descripción')),
                ('imagen', models.FileField(default='', upload_to='fotos/', verbose_name='Imagen')),
                ('fecha_publicacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Publicación')),
            ],
            options={
                'verbose_name': 'Publicación',
                'verbose_name_plural': 'Publicaciones',
                'ordering': ['-fecha_publicacion'],
            },
        ),
    ]
