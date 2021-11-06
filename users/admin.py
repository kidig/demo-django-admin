from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as BaseGroup
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.core import serializers
from django.db.models import Value
from django.db.models.functions import Concat
from django.http import HttpResponse

User = get_user_model()

admin.site.unregister(BaseGroup)
admin.site.site_header = _("Django Admin Demo")


"""
Массовые операции со списком объектов можно выносить в отдельные функции, чтобы переиспользовать
"""
@admin.action(
    description="Сделать активными",
)
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(
    description="Сделать не активными",
)
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    list_display = (
        "username", "email", "full_name",
        "is_active", "is_superuser", "is_staff",
        "date_joined", "last_login",
    )

    """
    ссылку на редактирование объектов можно поставить не только на первое поле в списке,
    но и на любые другие
    """
    list_display_links = ("username", "email",)

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
    )
    search_fields = ("username", "email", "first_name", "last_name")
    date_hierarchy = "date_joined"

    """
    определяет какие массовые операции будут доступны в админке.
    
    плюс, по умолчанию всегда есть операция по удалению объектов.
    """
    actions = [
        make_active,
        make_inactive,
        "export_as_json",
    ]

    """
    у базового класса UserAdmin уже определены fieldsets, но это не мешает добавить что-нибудь ещё
    """
    fieldsets = (*auth_admin.UserAdmin.fieldsets, (_("Ссылки"), {"fields": ("link_to_posts", )}))
    readonly_fields = ('last_login', "link_to_posts")

    """
    дополнительные поля можно собирать из существующих,
    и чтобы иметь возможность сортировки `ordering`, нужно также сделать "склейку" на уровне БД
    """
    @admin.display(
        description=_("Полное имя"),
        ordering=Concat('first_name', Value(' '), 'last_name'),
    )
    def full_name(self, obj: User):
        return f"{obj.first_name} {obj.last_name}"

    """
    добавляет стандартный экспорт данных в JSON
    """
    @admin.action(
        description=_("Экспорт в JSON"),
    )
    def export_as_json(self, request, queryset):
        response = HttpResponse(content_type="application/json")
        serializers.serialize("json", queryset, stream=response)
        return response

    """
    чтобы показать большой набор связанных данных, вместо inlines,
    можно сформировать ссылку на другую админку с фильтром.
    
    например, отфильтровать посты по автору: `?author_id=<obj_id>`  
    """
    @admin.display(
        description=_("Все посты пользователя"),
    )
    def link_to_posts(self, obj: User):
        return format_html(
            '<a href="{}?{}" target="_blank">Посмотреть ({})</a>',
            reverse("admin:content_post_changelist"),
            "author_id={}".format(obj.pk),
            obj.posts.count(),
        )