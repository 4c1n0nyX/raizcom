from django.db import models
from django.conf import settings
from django.db.models import Count
from datetime import datetime

# =============== MODELO SALAS DE CHAT ============== #
class ChatRoom(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms', blank=True)
    ROOM_TYPE_CHOICES = [
        ('private', 'Chat Privado'),
        ('general', 'Chat General'),
        ('group', 'Chat de Grupo'),
    ]
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='private', help_text="Tipo de sala de chat (privado, general, de grupo).")
    name = models.CharField(max_length=255, unique=False, null=True, blank=True, help_text="Nombre de la sala (para chats generales/de grupo).")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] 
        constraints = [
            models.UniqueConstraint(fields=['room_type', 'name'], condition=models.Q(room_type='general'), name='unique_general_room_name',)
        ]

    def __str__(self):
        if self.name:
            return f"Sala: {self.name} (ID: {self.id}, Tipo: {self.room_type})"

        if self.room_type == 'private':
            participant_usernames = list(self.participants.all().values_list('username', flat=True))
            if len(participant_usernames) == 2:
                return f"Chat Privado: {participant_usernames[0]} y {participant_usernames[1]} (ID: {self.id})"
            elif len(participant_usernames) == 1:
                return f"Chat Privado (incompleto) con {participant_usernames[0]} (ID: {self.id})"
            else:
                return f"Chat Privado con {len(participant_usernames)} participantes (ID: {self.id})"
        
        return f"Sala de Chat (Tipo: {self.room_type}, ID: {self.id})"

    @classmethod
    def get_or_create_private_room(cls, user1, user2):
        if user1.id > user2.id:
            user1, user2 = user2, user1

        room = cls.objects.annotate(num_participants=Count('participants')).filter(
            room_type='private',
            num_participants=2,
            participants=user1
        ).filter(
            participants=user2
        ).first()

        if not room:
            room = cls.objects.create(name=f"Chat {user1.username}-{user2.username}", room_type='private')
            room.participants.add(user1, user2)
            print(f"DEBUG: Created new private chat room: {room.name} (ID: {room.id})")
        else:
            print(f"DEBUG: Found existing private chat room: {room.name} (ID: {room.id})")
            
        return room

    @classmethod
    def get_general_chat_room(cls):
        general_room_name = "Sala General"
        general_room_type = 'general'

        general_room, created = cls.objects.get_or_create(
            name=general_room_name,
            room_type=general_room_type,
            defaults={'name': general_room_name, 'room_type': general_room_type}
        )
        
        if created:
            print(f"DEBUG: Created new general chat room: {general_room.name} (ID: {general_room.id})")
        else:
            print(f"DEBUG: Found existing general chat room: {general_room.name} (ID: {general_room.id})")
            
        return general_room

    @classmethod
    def get_alertas_chat_room(cls):
        alertas_room_name = "Alertas Bot"
        general_room_type = 'general'

        general_room, created = cls.objects.get_or_create(
            name=alertas_room_name,
            room_type=general_room_type,
            defaults={'name': alertas_room_name, 'room_type': general_room_type}
        )
        
        if created:
            print(f"DEBUG: Created new general chat room: {general_room.name} (ID: {general_room.id})")
        else:
            print(f"DEBUG: Found existing general chat room: {general_room.name} (ID: {general_room.id})")
            
        return general_room

    def get_participants_list(self):
        return list(self.participants.all())

    def get_other_user(self, current_user):
        if self.room_type == 'private' and self.participants.count() == 2:
            other_participant = self.participants.exclude(id=current_user.id).first()
            return other_participant
        return None

# =============== MODELO DE MENSAJES ============== #
class Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        room_identifier = self.chatroom.name if self.chatroom.name else f"ID: {self.chatroom.id}"
        return f"De {self.sender.username} en {room_identifier}: {self.content[:50]}..."
    
