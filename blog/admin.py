from django.contrib import admin
from .models import Category, Topic, Post

# Register your models here.
admin.site.register([Category, Topic, Post])
