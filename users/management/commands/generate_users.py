from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from users.factories import UserFactory


class Command(BaseCommand):
    help = _("Генерирует тестовых пользователей.")

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--count', dest='count', type=int, default=10,
            help=_("кол-во пользователей. по умолчанию - 10"),
        )

    def handle(self, *args, **options):
        count = options["count"]
        UserFactory.create_batch(count)
        self.stdout.write("Done\n")
