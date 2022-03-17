from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser


class Chat(models.Model):

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'



class CustomUser(AbstractUser):
    photo = models.ImageField(verbose_name='Фото')
    profile_type = models.CharField(verbose_name='Тип профиля', max_length=100)
    city = models.CharField(verbose_name='Город', max_length=100)
    interest = ArrayField(models.CharField(max_length=100), verbose_name='Интересы', blank=True, null=True)
    looking = ArrayField(models.CharField(max_length=100), verbose_name='Кого мы ищем', blank=True, null=True)

    first_name = models.CharField(verbose_name='Имя', max_length=100, blank=True, null=True)
    last_name = models.CharField(verbose_name='Фамилия', max_length=100, blank=True, null=True)
    middle_name = models.CharField(verbose_name='Отчество', max_length=100, blank=True, null=True)

    chats = models.ManyToManyField(Chat, through='ChatMember', blank=True, verbose_name='Чаты')

    company_name = models.CharField(verbose_name='Название компании', max_length=100, blank=True, null=True)
    company_description = models.TextField(verbose_name='Описание компании', blank=True, null=True)
    company_type = models.CharField(verbose_name='Тип компании', max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}'



class UserLike(models.Model):
    like_to = models.ForeignKey(CustomUser, related_name='likes_to', on_delete=models.CASCADE)
    like_from = models.ForeignKey(CustomUser, related_name='likes_from', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        unique_together = ('like_to', 'like_from')

    def __str__(self):
        return f'{self.like_to} оценил {self.like_from}'


class ChatMember(models.Model):
    chat = models.ForeignKey(Chat, related_name='members', on_delete=models.CASCADE, verbose_name='Чат')
    user = models.ForeignKey(CustomUser, related_name='members', on_delete=models.CASCADE, verbose_name='Участник чата')

    class Meta:
        verbose_name = 'Участник чата'
        verbose_name_plural = 'Участники чата'

    def __str__(self):
        return f'{self.user} участник {self.chat}'


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE, verbose_name='Чат')
    member = models.ForeignKey(CustomUser, related_name='messages', on_delete=models.CASCADE, verbose_name='Участник чата')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'От {self.member} в {self.chat}'

class Project(models.Model):
    user = models.ForeignKey(CustomUser, related_name='projects', on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(verbose_name='Название проекта', max_length=100)
    description = models.TextField(verbose_name='Описание проекта')
    investments = models.IntegerField(verbose_name='Инвестиции')
    profit = models.IntegerField(verbose_name='Доход')
    tags = ArrayField(models.CharField(max_length=100), verbose_name='Категории')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return f'{self.title}'


class ProjectLike(models.Model):
    user = models.ForeignKey(CustomUser, related_name='likes', on_delete=models.CASCADE, verbose_name='Пользователь')
    project = models.ForeignKey(Project, related_name='likes', on_delete=models.CASCADE, verbose_name='Проект')

    class Meta:
        verbose_name = 'Оценка проекту'
        verbose_name_plural = 'Оценки проектам'

    def __str__(self):
        return f'{self.user} оценил {self.project}'

class ProjectComment(models.Model):
    user = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE, verbose_name='Пользователь')
    project = models.ForeignKey(Project, related_name='comments', on_delete=models.CASCADE, verbose_name='Проект')
    text = models.TextField(verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Комментарий по проекту'
        verbose_name_plural = 'Комментарии по проектам'

    def __str__(self):
        return f'{self.user} прокомментировал {self.project}'


class ProjectNew(models.Model):
    user = models.ForeignKey(CustomUser, related_name='news', on_delete=models.CASCADE, verbose_name='Пользователь')
    project = models.ForeignKey(Project, related_name='news', on_delete=models.CASCADE, verbose_name='Проект')
    text = models.TextField(verbose_name='Новость')

    class Meta:
        verbose_name = 'Новость о проекте'
        verbose_name_plural = 'Новости о проектах'

    def __str__(self):
        return f'Новость от {self.user} о {self.project}'

