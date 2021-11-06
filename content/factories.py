import factory
import faker
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.text import slugify
from django.utils.timezone import make_aware
from factory.django import DjangoModelFactory
from text_unidecode import unidecode

from content.models import Blog, Post
from users.factories import UserFactory

User = get_user_model()
fake = faker.Faker(settings.FACTORY_BOY_DEFAULT_LOCALE)


class BlogFactory(DjangoModelFactory):
    class Meta:
        model = Blog

    name = factory.Faker("catch_phrase", locale=settings.FACTORY_BOY_DEFAULT_LOCALE)
    owner = factory.SubFactory(UserFactory)

    @factory.lazy_attribute
    def slug(self):
        return slugify(unidecode(self.name))

    @factory.lazy_attribute
    def created(self):
        return make_aware(fake.date_time_this_decade())


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    blog = factory.SubFactory(BlogFactory)
    author = factory.SubFactory(UserFactory)
    body = factory.Faker("text", locale=settings.FACTORY_BOY_DEFAULT_LOCALE)

    @factory.lazy_attribute
    def title(self):
        # убираем точку в конце
        return fake.sentence(nb_words=4).rstrip(".")

    @factory.lazy_attribute
    def created(self):
        return make_aware(fake.date_time_this_decade())
