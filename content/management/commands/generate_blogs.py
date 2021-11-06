from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from content.factories import BlogFactory


User = get_user_model()


class Command(BaseCommand):
    help = _("Генерирует тестовые блоги")

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--count', dest='count', type=int, default=10,
            help=_("кол-во блогов. по умолчанию - 10")
        )
        parser.add_argument(
            '-o', '--owner', dest="owner_id", type=int,
            help=_("ID владельца блога. если не указано, то будут созданы новые владельцы для каждого блога")
        )

    def handle(self, *args, **options):
        count = options["count"]
        owner_id = options.get("owner_id")

        kwargs = dict()

        if owner_id:
            kwargs["owner"] = User.objects.get(pk=owner_id)

        BlogFactory.create_batch(size=count, **kwargs)
        self.stdout.write("Done\n")
