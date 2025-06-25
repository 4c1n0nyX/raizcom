import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import ChatRoom, Message
User = get_user_model()

# =============== CONEXIONES DE SALAS DE CHAT ============== #
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"

        self.user = self.scope['user']

        if not self.user.is_authenticated:
            print("Conexión WebSocket rechazada: Usuario no autenticado.")
            await self.close()
            return

        try:
            self.chat_room = await sync_to_async(ChatRoom.objects.get)(id=self.room_id)
            
            if self.chat_room.room_type == 'private':
                is_participant = await sync_to_async(self.chat_room.participants.filter(id=self.user.id).exists)()
                if not is_participant:
                    print(f"Conexión WebSocket rechazada: Usuario {self.user.username} no es participante de la sala privada {self.room_id}.")
                    await self.close()
                    return
            
            if self.chat_room.room_type in ['general', 'group']:
                 await sync_to_async(self.chat_room.participants.add)(self.user)

        except ChatRoom.DoesNotExist:
            print(f"Conexión WebSocket rechazada: ChatRoom {self.room_id} no existe.")
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"Conexión WebSocket establecida para el usuario {self.user.username} en la sala {self.room_id}.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Conexión WebSocket cerrada para el usuario {self.user.username} de la sala {self.room_id} (Código: {close_code}).")


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']

        if not self.user.is_authenticated:
            return

        message_obj = await self.save_message(self.chat_room, self.user, message_content)
        
        sender_full_name = await self.get_sender_full_name(self.user)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_username': self.user.username,
                'sender_full_name': sender_full_name,
                'sender_id': self.user.id,
                'timestamp': message_obj.timestamp.isoformat(),
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_full_name = event['sender_full_name']
        sender_username = event['sender_username']
        sender_id = event['sender_id']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender_full_name': sender_full_name,
            'sender_username': sender_username,
            'sender_id': sender_id,
            'timestamp': timestamp,
        }))

    @sync_to_async
    def get_sender_full_name(self, user):
        if hasattr(user, 'nombre') and hasattr(user, 'apellido') and user.nombre and user.apellido:
            return f"{user.nombre} {user.apellido}"
        elif hasattr(user, 'first_name') and hasattr(user, 'last_name') and user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}"
        elif hasattr(user, 'nombre') and user.nombre:
            return user.nombre
        elif hasattr(user, 'first_name') and user.first_name:
            return user.first_name
        return user.username

    @sync_to_async
    def save_message(self, chatroom, sender, content):
        message_obj = Message.objects.create(chatroom=chatroom, sender=sender, content=content)
        return message_obj

