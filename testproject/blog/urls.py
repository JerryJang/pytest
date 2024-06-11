from django.urls import path
from . import views


# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PianoLessonViewSet, PianoNoteViewSet

router = DefaultRouter()
router.register(r'lessons', PianoLessonViewSet)
router.register(r'notes', PianoNoteViewSet)
from django.urls import path
from .views import PianoLessonListCreate, PianoLessonDetail



urlpatterns = [
    path('', views.index, name='index'),
    path('/sheet', include(router.urls)),
    path('pianolessons/', PianoLessonListCreate.as_view(), name='piano-lesson-list'),
    path('pianolessons/<int:pk>/', PianoLessonDetail.as_view(), name='piano-lesson-detail'),
    path('api/pianolessons/<int:pk>/', PianoLessonDetail.as_view(), name='pianolesson-detail'),
]