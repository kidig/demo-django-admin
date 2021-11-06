from django.contrib import admin
from django.db.models import Value
from django.db.models.functions import Concat
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .forms import BlogAdminForm
from .models import Blog, Post


# для создания админки этого уже достаточно,
# но можно значительно улучшить
#
# @admin.register(Blog)
# class BlogAdmin(admin.ModelAdmin):
#     pass


class PostInline(admin.TabularInline):
    """
    Определяем вид вложенных постов.
    Здесь можно указывать только необходимые поля, а также добавлять свои.

    Основной минус inlines - это отсутствие пагинации,
    все вложенные объекты будут располагаться на одной странице.

    Здесь вложенные посты показаны ради примера.
    В реальном проекте в inlines не нужно добавлять связанные модели с большим кол-вом объектов.
    """
    model = Post
    extra = 0
    raw_id_fields = ("author",)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("name", "owner_name", "is_published", "created", "modified")
    list_filter = ("is_published",)
    search_fields = (
        "name",
        "owner__username",
        "owner__first_name",
        "owner__last_name",
    )
    date_hierarchy = "created"

    form = BlogAdminForm

    """
    если этого не сделать, то в админке будет отрисован выпадающий список
    со всеми существующими пользователями, при их большом кол-ве - будут проблемы с производительностью,
    да и сам интерфейс будет притормаживать.
    
    поэтому делаем выбор пользователей во всплывающем окне.
    также можно использовать `autocompleted_fields`
    """
    raw_id_fields = ("owner",)

    """
    заполняем `slug`, используя значение из поля `name`
    """
    prepopulated_fields = {
        "slug": ("name",),
    }

    inlines = [
        PostInline,
    ]

    """
    при создании кастомного поля мы указываем его название,
    а также поле для сортировки (иначе просто по этому полю не получится отсортировать записи)
    
    при этом в `ordering` добавляем SQL ф-цию Concat, чтобы "склеить" поля на уровне бд и
    уже по полученным значениям выполнить сортировку
    """
    @admin.display(
        description=_("владелец"),
        ordering=Concat('owner__first_name', Value(' '), 'owner__last_name'),
    )
    def owner_name(self, obj: Blog):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:users_user_change", args=(obj.owner_id,)),
            obj.owner.get_full_name(),
        )

    """
    переопределяем сохранение модели, 
    чтобы при необходимости указать владельцем блога текущего пользователя 
    """
    def save_model(self, request, obj, form, change):
        if not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


class AuthorActiveListFilter(admin.BooleanFieldListFilter):
    """
    переопределяем стандартный фильтр BooleanFieldListFilter,
    просто чтобы поменять ему название :)

    тут не только красоты ради, но и для того чтобы показать,
    как можно менять логику фильтра
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = _("автор активен")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    указываем поля для списка
    """
    list_display = ("title", "author_link", "blog_link", "is_published", "created", "modified")

    """
    указываем фильтрацию по полям, и также можем применять свои фильтры
    """
    list_filter = ("is_published", ("author__is_active", AuthorActiveListFilter))

    """
    в `list_display` используем данные из связанных полей `author` и `blog`,
    дабы не создавать лишних запросов к базе - используем `select_related`
    
    данная настройка относится только к отрисовке списка объектов,
    если нужно оптимизировать запросы внутри формы редактирования,
    можно переопределить запрос в методе `get_queryset`
    """
    list_select_related = ("author", "blog")

    search_fields = (
        "title",
        "author__username",
        "author__first_name",
        "author__last_name",
    )

    """
    добавляем разбивку данных по дате
    """
    date_hierarchy = "created"

    """
    добавляем автоподстановку для полей `blog`, `author` при создании/редактировании объектов
    
    при этом для данных полей должны быть определены их собственные админки.
    """
    autocomplete_fields = ("blog", "author",)

    @admin.display(
        description=_("автор"),
        ordering="author__username",
    )
    def author_link(self, obj: Post):
        """
        кроме ссылки на админку пользователя,
        можно добавить стилизацию надписи, например, выделять неактивных авторов
        """
        return format_html(
            '<a href="{}" style="{}">{}</a>',
            reverse("admin:users_user_change", args=(obj.author_id,)),
            "text-decoration: line-through; color: grey" if not obj.author.is_active else "",
            obj.author,
        )

    """
    добавляет ссылку на блог
    
    для генерации ссылки использована ф-ция `reverse`,
    путь до любых админок можно составить по аналогии:
       
       "admin:<app>_<model>_change", args=(<model_id>,)
       
    для ссылки на список объектов:
    
       "admin:<app>_<model>_changelist" 
    """
    @admin.display(
        description=_("блог"),
        ordering="blog__name",
    )
    def blog_link(self, obj: Post):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:content_blog_change", args=(obj.blog_id,)),
            obj.blog,
        )