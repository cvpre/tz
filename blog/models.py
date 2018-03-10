import math

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import Truncator
from django.utils.html import mark_safe
from django.urls import reverse

from markdown import markdown


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    image = models.ImageField(upload_to='Category_img', blank=True)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__category=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__category=self).order_by('-created_at').first()


class Topic(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='topics')
    starter = models.ForeignKey(User, related_name='topics', on_delete=models.PROTECT)
    subject = models.CharField(max_length=255)
    last_updated = models.DateTimeField('date published', auto_now_add=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject

    def get_page_count(self):
        count = self.posts.count()
        pages = count / 20
        return math.ceil(pages)

    def has_many_pages(self, count=None):
        if count is None:
            count = self.get_page_count()
        return count > 6

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1, 5)
        return range(1, count + 1)

    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]


class Post(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='posts')
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.PROTECT)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.PROTECT)
    message = models.CharField(max_length=4000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    custom_name = models.CharField(max_length=25, null=True, blank=True)
    site = models.CharField(max_length=40, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))

    def get_absolute_url(self):
        return reverse("blog:topic_posts", kwargs={'category_pk': self.topic.category.pk, 'topic_pk': self.topic_id})
