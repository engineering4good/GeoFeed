from django.contrib import admin

from .models import Feed
from .models import Message

admin.site.register(Feed)
admin.site.register(Message)
