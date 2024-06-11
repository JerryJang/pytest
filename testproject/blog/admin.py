from django.contrib import admin
from .models import Post, Audio, PianoLesson, PianoNote

admin.site.register(Post)
admin.site.register(Audio)
admin.site.register(PianoLesson)
admin.site.register(PianoNote)