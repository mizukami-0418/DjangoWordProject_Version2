# flashcard/api_urls.py

from django.urls import path
from .api_views import (
    UserProgressListAPIView,
    UserProgressDetailAPIView,
    start_quiz,
    submit_answer,
    pause_quiz,
    resume_quiz,
    delete_progress,
    get_statistics,
    get_incorrect_words,
)

app_name = "flashcard_api"

urlpatterns = [
    # 進行状況
    path("progress/", UserProgressListAPIView.as_view(), name="progress_list"),
    path(
        "progress/<int:pk>/",
        UserProgressDetailAPIView.as_view(),
        name="progress_detail",
    ),
    path("progress/<int:progress_id>/pause/", pause_quiz, name="pause_quiz"),
    path("progress/<int:progress_id>/resume/", resume_quiz, name="resume_quiz"),
    path("progress/<int:progress_id>/delete/", delete_progress, name="delete_progress"),
    # クイズ
    path("quiz/start/", start_quiz, name="start_quiz"),
    path("quiz/answer/", submit_answer, name="submit_answer"),
    # 統計
    path("statistics/", get_statistics, name="statistics"),
    path("incorrect-words/", get_incorrect_words, name="incorrect_words"),
]
