from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Chat(models.Model):
    members = models.ManyToManyField(User, related_name="chats")

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
