from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Chat(models.Model):
    members = models.ManyToManyField(User, related_name="chats")

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Сообщение")
    timestamp = models.DateTimeField(verbose_name="Дата публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self) -> str:
        return self.author.email
