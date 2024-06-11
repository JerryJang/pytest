from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from rest_framework import generics
from rest_framework.views import APIView

from .forms import AudioForm
from .speech_recognition import recognize_notes
from .models import PianoLesson
from .serializers import PianoLessonSerializer

# views.py
from rest_framework import viewsets
from .models import PianoLesson, PianoNote
from .serializers import PianoLessonSerializer, PianoNoteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PianoLesson
from .serializers import PianoLessonSerializer


class PianoLessonDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            lesson = PianoLesson.objects.get(pk=pk)
        except PianoLesson.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PianoLessonSerializer(lesson)
        return Response(serializer.data)

class PianoLessonViewSet(viewsets.ModelViewSet):
    queryset = PianoLesson.objects.all()
    serializer_class = PianoLessonSerializer

class PianoNoteViewSet(viewsets.ModelViewSet):
    queryset = PianoNote.objects.all()
    serializer_class = PianoNoteSerializer

class PianoLessonListCreate(generics.ListCreateAPIView):
    queryset = PianoLesson.objects.all()
    serializer_class = PianoLessonSerializer

class PianoLessonDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PianoLesson.objects.all()
    serializer_class = PianoLessonSerializer


def index(request):
    notes = []
    if request.method == 'POST':
        form = AudioForm(request.POST, request.FILES)
        if form.is_valid():
            audio_file = form.cleaned_data['file']
            from django.core.files.base import ContentFile
            file_name = default_storage.save(audio_file.name, ContentFile(audio_file.read()))
            audio_path = default_storage.path(file_name)
            print(f"Uploaded file path: {audio_path}")
            try:
                notes = recognize_notes(audio_path)
                print(f"Recognized notes: {notes}")
            except Exception as e:
                # 오류 처리
                print(e)
            return redirect('index')
        else:
            print('Form is not valid:', form.errors)
    else:
        form = AudioForm()
    return render(request, 'blog/index.html', {'form': form, 'notes': notes})
