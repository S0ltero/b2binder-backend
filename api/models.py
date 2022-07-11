from django.core import validators
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser

from .managers import UserManager


class CustomUser(AbstractUser):
    username = None

    email = models.EmailField(
        "Email-адрес",
        unique=True,
        validators=[validators.validate_email],
        error_messages={
            "unique": "Пользователь с таким email уже существует.",
        },
    )

    photo = models.ImageField(verbose_name="Фото", blank=True, null=True)
    authorization = models.FileField(verbose_name="Авторизация", blank=True, null=True)
    country = models.CharField(verbose_name="Страна", max_length=100)
    city = models.CharField(verbose_name="Город", max_length=100)
    interest = ArrayField(models.CharField(max_length=100), verbose_name="Интересы")
    looking = ArrayField(models.CharField(max_length=100), verbose_name="Кого мы ищем")

    first_name = models.CharField(verbose_name="Имя", max_length=100)
    last_name = models.CharField(verbose_name="Фамилия", max_length=100)
    middle_name = models.CharField(verbose_name="Отчество", max_length=100, blank=True)

    company_name = models.TextField(verbose_name="Название компании")
    company_description = models.TextField(verbose_name="Описание компании")
    company_type = models.CharField(verbose_name="Тип компании", max_length=100)

    likes_from = models.ManyToManyField(
        "self", related_name="likes_to", through="UserLike", symmetrical=False
    )
    like_projects = models.ManyToManyField(
        "Project", related_name="likes", through="ProjectLike"
    )

    subscriptions = models.ManyToManyField(
        "self", related_name="subscribers", through="UserSubscribe", symmetrical=False
    )

    online = models.BooleanField(verbose_name="Статус", default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ()

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.email}"


class UserLike(models.Model):
    like_to = models.ForeignKey(CustomUser, related_name="+", on_delete=models.CASCADE)
    like_from = models.ForeignKey(
        CustomUser, related_name="+", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        unique_together = ("like_to", "like_from")

    def __str__(self):
        return f"{self.like_from} оценил {self.like_to}"


class UserSubscribe(models.Model):
    subscriber = models.ForeignKey(
        CustomUser, related_name="+", on_delete=models.CASCADE, verbose_name="Подписчик"
    )
    subscription = models.ForeignKey(
        CustomUser, related_name="+", on_delete=models.CASCADE, verbose_name="Подписка"
    )

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
        unique_together = ("subscriber", "subscription")

    def __str__(self):
        return f"{self.subscriber}, {self.subscription}"


class Category(models.Model):
    name = models.CharField(verbose_name="Название категории", max_length=100)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return f"{self.name}"


class Project(models.Model):
    class Type(models.TextChoices):
        VENTURE = "VENTRUE", "Венчурная сделка"
        COLLECTIVE = "COLLECTIVE", "Коллективная сделка"
        JOINT = "JOINT", "Совместные инвестиции"
        SALE = "SALE", "Продажа доли"

    user = models.ForeignKey(
        CustomUser,
        related_name="projects",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    type = models.CharField(verbose_name="Тип проекта", max_length=100, choices=Type.choices)
    title = models.CharField(verbose_name="Название проекта", max_length=100)
    description = models.TextField(verbose_name="Описание проекта")
    short_description = models.CharField(
        verbose_name="Краткое описание", max_length=255
    )
    image = models.ImageField(verbose_name="Изображение проекта", blank=True, null=True)
    investments = models.IntegerField(verbose_name="Инвестиции")
    profit = models.IntegerField(verbose_name="Доход")
    categories = models.ManyToManyField(
        Category, verbose_name="Категории", related_name="projects", blank=True
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return f"{self.title}"


class ProjectLike(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name="+",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    project = models.ForeignKey(
        Project, related_name="+", on_delete=models.CASCADE, verbose_name="Проект"
    )

    class Meta:
        verbose_name = "Оценка проекту"
        verbose_name_plural = "Оценки проектам"
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user} оценил {self.project}"


class ProjectComment(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    project = models.ForeignKey(
        Project,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="Проект",
    )
    text = models.TextField(verbose_name="Комментарий")

    class Meta:
        verbose_name = "Комментарий по проекту"
        verbose_name_plural = "Комментарии по проектам"

    def __str__(self):
        return f"{self.user} прокомментировал {self.project}"


class ProjectNew(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name="news",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    project = models.ForeignKey(
        Project, related_name="news", on_delete=models.CASCADE, verbose_name="Проект"
    )
    text = models.TextField(verbose_name="Новость")

    class Meta:
        verbose_name = "Новость о проекте"
        verbose_name_plural = "Новости о проектах"

    def __str__(self):
        return f"Новость от {self.user} о {self.project}"


class ProjectOffer(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name="offers",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    project = models.ForeignKey(
        Project, related_name="offers", on_delete=models.CASCADE, verbose_name="Проект"
    )
    amount = models.PositiveIntegerField(verbose_name="Размер инвестиции")

    class Meta:
        verbose_name = "Инвестиция"
        verbose_name_plural = "Инвестиции"

    def __str__(self):
        return f"Инвестиция от {self.user} в {self.project}"


class Callback(models.Model):
    first_name = models.CharField(verbose_name="Имя", max_length=100)
    last_name = models.CharField(verbose_name="Фамилия", max_length=100)
    email = models.EmailField(verbose_name="Электронная почта")
    text = models.TextField(verbose_name="Текст обращения")

    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратная связь"

    def __str__(self):
        return f"{self.email}"
