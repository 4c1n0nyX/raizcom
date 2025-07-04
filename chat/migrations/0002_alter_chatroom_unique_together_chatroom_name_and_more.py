# Generated by Django 5.2.3 on 2025-06-17 19:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='chatroom',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='name',
            field=models.CharField(blank=True, help_text='Nombre de la sala (para chats generales/de grupo).', max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='chat_rooms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='room_type',
            field=models.CharField(choices=[('private', 'Chat Privado'), ('general', 'Chat General'), ('group', 'Chat de Grupo')], default='private', help_text='Tipo de sala de chat (privado, general, de grupo).', max_length=10),
        ),
        migrations.RemoveField(
            model_name='chatroom',
            name='user1',
        ),
        migrations.RemoveField(
            model_name='chatroom',
            name='user2',
        ),
    ]
