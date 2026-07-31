from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def _send(group_name: str, payload: dict):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "task_message",
            "payload": payload,
        },
    )


def push_to_task(task_id: str, payload: dict):
    _send(f"task_{task_id}", payload)


def push_to_user(user_id: str, payload: dict):
    _send(f"user_{user_id}", payload)


def push_ws(task_id: str, user_id: str | None, payload: dict):
    payload = dict(payload)
    payload.setdefault("taskId", task_id)
    push_to_task(task_id, payload)
    if user_id:
        push_to_user(user_id, payload)