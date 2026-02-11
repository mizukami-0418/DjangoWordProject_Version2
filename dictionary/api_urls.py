# dictionary/api_urls.py

from django.urls import path
from .api_views import (
    WordListAPIView,
    WordDetailAPIView,
    word_search,
    LevelListAPIView,
    PartOfSpeechListAPIView,
    word_random,
)

app_name = "dictionary_api"

urlpatterns = [
    # 単語関連
    path("words/", WordListAPIView.as_view(), name="word_list"),
    path("words/<int:pk>/", WordDetailAPIView.as_view(), name="word_detail"),
    path("words/random/", word_random, name="word_random"),
    # 検索
    path("search/", word_search, name="word_search"),
    # マスターデータ
    path("levels/", LevelListAPIView.as_view(), name="level_list"),
    path(
        "parts-of-speech/",
        PartOfSpeechListAPIView.as_view(),
        name="part_of_speech_list",
    ),
]
