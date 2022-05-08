import json
from typing import List

from django.db.models import Count
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin, action
from djangochannelsrestframework.observer import model_observer

from api.models import CustomUser
from api.serializers import UserSerializer

from .models import Chat, Message
from .serializers import ChatSerializer, ChatDetailSerializer, MessageSerializer


User = get_user_model()


class ChatConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Chat.objects.all()
    serializer_class = ChatDetailSerializer
    lookup_field = "pk"

    @action()
    async def get_my_chats(self, request_id, **kwargs):
        user: CustomUser = self.scope["user"]
        chats = await self.get_user_chats(user)
        await self.send_json({"data": chats, "action": "get_my_chats", "request_id": request_id})

    @action()
    async def add_chat(self, request_id, user_id, **kwargs):
        sender: CustomUser = self.scope["user"]
        recepient: CustomUser = await self.get_user(user_id)
        chat = await self.get_chat_by_members(members=[sender, recepient])
        if not chat:
            chat: Chat = await self.create_chat()
            await self.add_user_to_chat(chat, sender)
            await self.add_user_to_chat(chat, recepient)

        self.chat_pk = chat.id
        await self.send_json(
            {"chat_id": self.chat_pk, "action": "add_chat", "request_id": request_id}
        )

    @action()
    async def join_chat(self, request_id, chat_id, **kwargs):
        user: CustomUser = self.scope["user"]
        try:
            chat = await self.get_user_chat(user=user, pk=chat_id)
        except Chat.DoesNotExist:
            return await self.send_json(
                {
                    "action": "join_chat",
                    "request_id": request_id,
                    "exception": "У вас нет доступа к данному чату"
                }
            )

        self.chat_pk = chat.id
        await self.send_json(
            {
                "chat_id": self.chat_pk,
                "action": "join_chat",
                "request_id": request_id
            }
        )

    @action()
    async def create_message(self, message, **kwargs):
        chat: Chat = await self.get_chat(pk=kwargs["chat_id"])
        user: CustomUser = self.scope["user"]
        await database_sync_to_async(Message.objects.create)(
            chat=chat,
            author=user,
            content=message
        )

    @action()
    async def subscribe_to_messages_in_chat(self, pk, request_id, **kwargs):
        await self.message_activity.subscribe(chat=pk, request_id=request_id)

    @action()
    async def subscribe_to_messages_in_my_chats(self, request_id, **kwargs):
        user: CustomUser = self.scope["user"]
        for chat in user.chats:
            await self.message_activity.subscribe(chat=chat.pk, request_id=request_id)

    @model_observer(Message)
    async def message_activity(
        self,
        message,
        observer=None,
        subscribing_request_ids = [],
        **kwargs
    ):
        """
        This is evaluated once for each subscribed consumer.
        The result of `@message_activity.serializer` is provided here as the message.
        """
        # since we provide the request_id when subscribing we can just loop over them here.
        for request_id in subscribing_request_ids:
            message_body = dict(request_id=request_id)
            message_body.update(message)
            await self.send_json(message_body)

    @message_activity.groups_for_signal
    def message_activity(self, instance: Message, **kwargs):
        yield f'chat__{instance.chat_id}'
        yield f'pk__{instance.pk}'

    @message_activity.groups_for_consumer
    def message_activity(self, chat=None, **kwargs):
        if chat is not None:
            yield f'chat__{chat}'

    @message_activity.serializer
    def message_activity(self, instance:Message, action, **kwargs):
        """
        This is evaluated before the update is sent
        out to all the subscribing consumers.
        """
        return dict(data=MessageSerializer(instance).data, action=action.value, pk=instance.pk)

    async def update_users(self, event: dict):
        await self.send(text_data=json.dumps({'usuarios': event["usuarios"]}))

    @database_sync_to_async
    def get_chat(self, pk: int) -> Chat:
        return Chat.objects.get(pk=pk)

    @database_sync_to_async
    def get_user_chat(self, user: CustomUser, pk: int) -> Chat:
        return user.chats.get(pk=pk)

    @database_sync_to_async
    def get_chat_by_members(self, members: List[CustomUser]) -> Chat:
        chat = Chat.objects.filter(
            members__in=members
        ).annotate(
            id_count=Count("id")
        ).filter(
            id_count__gt=1
        ).first()
        return chat

    @database_sync_to_async
    def create_chat(self) -> Chat:
        return Chat.objects.create()

    @database_sync_to_async
    def get_user(self, pk: int) -> CustomUser:
        return CustomUser.objects.get(pk=pk)

    @database_sync_to_async
    def add_user_to_chat(self, chat: Chat, user: CustomUser = None):
        if not user.chats.filter(pk=chat.pk).exists():
            user.chats.add(chat)

    @database_sync_to_async
    def get_user_chats(self, user: CustomUser):
        serializer = ChatSerializer(user.chats, many=True, context={"scope": self.scope})
        return serializer.data


class UserConsumer(GenericAsyncAPIConsumer):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"

    async def connect(self):
        user = self.scope["user"]
        await self.set_user_status(user=user, status=1)
        await super().connect()

    async def disconnect(self, code):
        user = self.scope["user"]
        await self.set_user_status(user=user, status=0)
        await super().disconnect(code)

    @database_sync_to_async
    def set_user_status(self, user: CustomUser, status: bool):
        user.online = status
        user.save()
