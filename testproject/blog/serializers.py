# serializers.py
from rest_framework import serializers
from .models import PianoLesson, PianoNote

class PianoNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PianoNote
        fields = ['id', 'title', 'sheet_music']

class PianoLessonSerializer(serializers.ModelSerializer):
    notes = PianoNoteSerializer(many=True)
    class Meta:
        model = PianoLesson
        fields = '__all__'

