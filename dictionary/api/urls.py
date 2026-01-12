# dictionary/api/urls.py
from django.urls import path
from .views import WordListAPIView

urlpatterns = [
    path("words/", WordListAPIView.as_view()),
]
