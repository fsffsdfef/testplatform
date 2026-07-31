import json
from channels.generic.websocket import AsyncWebsocketConsumer


class BaseTaskConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data=None, bytes_data=None):
        if text_data == "ping":
            await self.send(text_data="pong")

    async def task_message(self, event):
        await self.send(text_data=json.dumps(event["payload"], ensure_ascii=False))


class UserChannelConsumer(BaseTaskConsumer):
    """用户级通道：接收 Beat 定时任务 + 手动执行推送"""

    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = f"user_{self.user_id}"
        user = self.scope.get("user")

        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        token_user_id = getattr(user, "userId", None)
        if str(token_user_id) != str(self.user_id):
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "connected",
            "userId": self.user_id,
            "msg": "用户 WebSocket 已连接",
        }, ensure_ascii=False))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)


class TaskChannelConsumer(BaseTaskConsumer):
    """任务级通道：单次执行订阅"""

    async def connect(self):
        self.task_id = self.scope["url_route"]["kwargs"]["task_id"]
        self.group_name = f"task_{self.task_id}"
        user = self.scope.get("user")

        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "connected",
            "taskId": self.task_id,
            "msg": "任务 WebSocket 已连接",
        }, ensure_ascii=False))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)