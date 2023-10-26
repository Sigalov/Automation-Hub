# your_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ConsoleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.block_id = self.scope['url_route']['kwargs']['block_id']
        await self.channel_layer.group_add(
            f"log_{self.block_id}",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"log_{self.block_id}",
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            f"log_{self.block_id}",
            {
                'type': 'log_message',
                'message': message
            }
        )

    async def log_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
