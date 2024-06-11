from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
class Audio(models.Model):
    file = models.FileField(upload_to='audio/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class PianoLesson(models.Model):
    image = models.FileField(upload_to='image/')
    uploaded_at2 = models.DateTimeField(auto_now_add=True)

    sheet_music = models.FileField(upload_to='sheet_music/')
    created_at = models.DateTimeField(auto_now_add=True)

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    playTime = models.TimeField
    sheetInfo = models.TextField

    def __str__(self):
        return self.title

class PianoNote(models.Model):
    lesson = models.ForeignKey(PianoLesson, related_name='notes', on_delete=models.CASCADE)
    note = models.CharField(max_length=1000)