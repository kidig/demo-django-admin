from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import models
from model_utils.models import TimeStampedModel

User = get_user_model()


class Blog(TimeStampedModel):
    """
    Блог для публикаций
    """
    owner = models.ForeignKey(
        User,
        verbose_name=_("владелец"),
        related_name="blogs",
        on_delete=models.CASCADE,
    )

    name = models.CharField(_("название"), max_length=255)
    slug = models.SlugField(_("ссылка"), blank=True)

    is_published = models.BooleanField(_("опубликован"), default=True)

    class Meta:
        ordering = ("-created",)
        verbose_name = _("блог")
        verbose_name_plural = _("блоги")

    def __str__(self):
        return f"{self.name} [{self.slug}]" if self.slug else self.name


class Post(TimeStampedModel):
    """
    Публикации в блогах, при этом можно указать другого автора
    """
    blog = models.ForeignKey(
        Blog,
        verbose_name=_("блог"),
        related_name="posts",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name=_("автор"),
        related_name="posts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    title = models.CharField(_("заголовок"), max_length=255)
    body = models.TextField(_("текст"))

    is_published = models.BooleanField(_("опубликован"), default=True)

    class Meta:
        ordering = ("-created",)
        verbose_name = _("пост")
        verbose_name_plural = _("посты")

    def __str__(self):
        return f"{self.title} [{self.pk}]"

    def save(self, *args, **kwargs):
        if not self.author:
            self.author = self.blog.owner
        super().save(*args, **kwargs)