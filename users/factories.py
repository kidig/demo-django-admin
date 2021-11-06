import random

import factory
import faker
from django.contrib.auth import get_user_model
from django.conf import settings
from factory.django import DjangoModelFactory
from django.utils.timezone import make_aware

User = get_user_model()
fake = faker.Faker(settings.FACTORY_BOY_DEFAULT_LOCALE)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username', 'email',)

    class Params:
        sex = random.choice(["male", "female"])

    username = factory.Sequence(lambda n: f"{fake.user_name()}-{n}")
    email = factory.Sequence(lambda n: f"{n}-{fake.email()}")

    @factory.lazy_attribute
    def first_name(self):
        method_name = f"first_name_{self.sex}" if self.sex else "first_name"
        return getattr(fake, method_name)()

    @factory.lazy_attribute
    def last_name(self):
        method_name = f"last_name_{self.sex}" if self.sex else "last_name"
        return getattr(fake, method_name)()

    @factory.lazy_attribute
    def date_joined(self):
        return make_aware(fake.date_time_this_decade())
