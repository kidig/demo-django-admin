from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from django.core.management.base import BaseCommand

from content.factories import PostFactory, BlogFactory
from content.models import Blog

User = get_user_model()


class Command(BaseCommand):
    help = _("Генерирует тестовые посты")

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--count', dest='count', type=int, default=10,
            help=_("кол-во записей. по умолчанию - 10")
        )
        parser.add_argument(
            '-b', dest="blog_id", type=int,
            help=_("ID блога, в котором будут созданы посты")
        )
        parser.add_argument(
            '-nb' '--num-blogs', dest="num_blogs", type=int,
            help=_("кол-во новых блогов. если не указано, то каждый пост будет создан в отдельном блоге")
        )
        parser.add_argument(
            '--author', dest="author_id", type=int,
            help=_("ID автора поста. если не указано, то будут созданы новые авторы.")
        )

    def create_posts(self, size, **kwargs):
        PostFactory.create_batch(size, **kwargs)

    def handle(self, *args, **options):
        count = options["count"]
        blog_id = options.get("blog_id")
        author_id = options.get("author_id")
        num_blogs = options.get("num_blogs")

        kwargs = dict()

        if author_id:
            """
            автор будет задан один для всех постов
            """
            kwargs["author"] = User.objects.get(pk=author_id)

        if num_blogs:
            """
            создаем нужное кол-во блогов,
            и в каждом генерируем публикации
            """
            blogs = BlogFactory.create_batch(num_blogs)
            for blog in blogs:
                kwargs["blog"] = blog
                self.create_posts(count, **kwargs)
        else:
            """
            если указан blog_id - то все посты будут созданы в нем.
            иначе - на каждый пост будет создан отдельный блог.
            """
            if blog_id:
                kwargs["blog"] = Blog.objects.get(pk=blog_id)

            self.create_posts(count, **kwargs)

        self.stdout.write("Done\n")
