from django.urls import path
from . import views


urlpatterns = [
    path('select_quiz/', views.select_quiz, name='select_quiz'),
    path('select_level/', views.select_level, name='select_level'),
    path('select_mode/', views.select_mode, name='select_mode'),
    # path('select_num_questions/', views.select_num_questions, name='select_num_questions'),
    path('quiz/', views.quiz, name='quiz'),
    path('quiz/restart/<int:progress_id>/', views.quiz_restart, name='quiz_restart'),
    path('check_answer/<int:progress_id>/', views.check_answer, name='check_answer'),
    path('result/<int:progress_id>/', views.result, name='result'),
    path('pause_quiz/<int:progress_id>/', views.pause_quiz, name='pause_quiz'),
    path('start_review/', views.start_review, name='start_review'),
    path('review_quiz/<int:review_id>/', views.review_quiz, name='review_quiz'),
    path('check_review_answer/<int:progress_id>/', views.check_review_answer, name='check_review_answer'),
    path('review_result/<int:progress_id>/', views.review_result, name='review_result'),
    path('pause_review/<int:progress_id>/', views.pause_review, name='pause_review'),
    path('reset_user_progress/<int:progress_id>/', views.reset_user_progress, name='reset_user_progress'),
    path('reset_review_progress/<int:progress_id>/', views.reset_review_progress, name='reset_review_progress'),
]
