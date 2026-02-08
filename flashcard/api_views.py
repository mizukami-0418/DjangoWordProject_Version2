# flashcard/api_views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
import random
import json

from .models import UserProgress, UserWordStatus, UserReviewProgress
from dictionary.models import Word, Level
from .serializers import (
    UserProgressSerializer,
    UserProgressCreateSerializer,
    UserWordStatusSerializer,
    AnswerSubmitSerializer,
    UserReviewProgressSerializer,
    StatisticsSerializer,
)


class UserProgressListAPIView(generics.ListAPIView):
    """
    ユーザーの進行状況一覧を取得

    GET /api/flashcard/progress/
    クエリパラメータ:
    - is_completed: 完了フラグでフィルタ（true/false）
    - is_paused: 中断フラグでフィルタ（true/false）
    """

    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = UserProgress.objects.filter(user=self.request.user).select_related(
            "level"
        )

        # 完了フラグでフィルタ
        is_completed = self.request.query_params.get("is_completed")
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == "true")

        # 中断フラグでフィルタ
        is_paused = self.request.query_params.get("is_paused")
        if is_paused is not None:
            queryset = queryset.filter(is_paused=is_paused.lower() == "true")

        return queryset.order_by("-completed_at")


class UserProgressDetailAPIView(generics.RetrieveAPIView):
    """
    進行状況の詳細を取得

    GET /api/flashcard/progress/<id>/
    """

    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user).select_related(
            "level"
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_quiz(request):
    """
    クイズを開始

    POST /api/flashcard/quiz/start/
    Body:
    {
        "level_id": 1,
        "mode": "en",  // en: 英訳, jp: 和訳
        "quiz_mode": "normal"  // normal: 通常, test: テスト, replay: リプレイ
    }
    """
    serializer = UserProgressCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    level_id = data["level_id"]
    mode = data["mode"]
    quiz_mode = data.get("quiz_mode", "normal")

    # レベルを取得
    level = get_object_or_404(Level, id=level_id)

    # 選択したレベルの単語を取得
    words = Word.objects.filter(level=level)

    # クイズモードによって問題を生成
    if quiz_mode == "test":
        # テストモード: ランダムで100問
        total_questions = min(100, words.count())
        questions = random.sample(
            list(words.values_list("id", flat=True)), total_questions
        )

    elif quiz_mode == "replay":
        # リプレイモード: 間違えた問題のみ
        incorrect_word_ids = UserWordStatus.objects.filter(
            user=request.user, mode=mode, is_correct=False
        ).values_list("word_id", flat=True)

        replay_words = words.filter(id__in=incorrect_word_ids)

        if not replay_words.exists():
            return Response(
                {
                    "error": "リプレイする問題がありません。まず通常モードで学習してください。"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_questions = replay_words.count()
        questions = random.sample(
            list(replay_words.values_list("id", flat=True)), total_questions
        )

    else:
        # 通常モード: 全問題
        total_questions = words.count()
        questions = random.sample(
            list(words.values_list("id", flat=True)), total_questions
        )

    # 進行状況を作成
    user_progress = UserProgress.objects.create(
        user=request.user,
        level=level,
        mode=mode,
        score=0,
        total_questions=total_questions,
        current_question_index=0,
        question_ids=json.dumps(questions),
    )

    # 最初の問題を取得
    first_question_id = questions[0]
    first_question = Word.objects.get(id=first_question_id)

    return Response(
        {
            "progress": UserProgressSerializer(user_progress).data,
            "current_question": {
                "id": first_question.id,
                "question": first_question.japanese
                if mode == "en"
                else first_question.english,
                "question_number": 1,
                "total_questions": total_questions,
            },
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    """
    回答を送信

    POST /api/flashcard/quiz/answer/
    Body:
    {
        "progress_id": 123,
        "answer": "apple"
    }

    Response:
    {
        "is_correct": true,
        "correct_answer": "apple",
        "score": 5,
        "current_question_index": 5,
        "is_completed": false,
        "next_question": { ... } または null（完了時）
    }
    """
    serializer = AnswerSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    progress_id = serializer.validated_data["progress_id"]
    answer = serializer.validated_data["answer"].strip()

    # 進行状況を取得
    user_progress = get_object_or_404(
        UserProgress, id=progress_id, user=request.user, is_completed=False
    )

    # 現在の問題を取得
    questions = json.loads(user_progress.question_ids)
    current_question_id = questions[user_progress.current_question_index]
    current_question = get_object_or_404(Word, id=current_question_id)

    # 正解を判定
    if user_progress.mode == "en":
        # 英訳モード
        correct_answer = current_question.english
        is_correct = answer == correct_answer
    else:
        # 和訳モード（複数の正解がカンマ区切りで存在する可能性）
        correct_answers = [ans.strip() for ans in current_question.japanese.split(",")]
        is_correct = answer in correct_answers
        correct_answer = current_question.japanese

    # スコアを更新
    if is_correct:
        user_progress.score += 1

    # UserWordStatusを更新または作成
    user_word_status, _ = UserWordStatus.objects.update_or_create(
        user=request.user,
        word=current_question,
        mode=user_progress.mode,
        defaults={"is_correct": is_correct},
    )

    # 問題インデックスを進める
    user_progress.current_question_index += 1

    # 完了判定
    is_completed = user_progress.current_question_index >= user_progress.total_questions

    if is_completed:
        user_progress.is_completed = True
        user_progress.is_paused = False
        user_progress.save()

        return Response(
            {
                "is_correct": is_correct,
                "correct_answer": correct_answer,
                "score": user_progress.score,
                "total_questions": user_progress.total_questions,
                "current_question_index": user_progress.current_question_index,
                "is_completed": True,
                "correct_rate": round(
                    user_progress.score / user_progress.total_questions * 100, 1
                ),
                "next_question": None,
            }
        )

    else:
        user_progress.save()

        # 次の問題を取得
        next_question_id = questions[user_progress.current_question_index]
        next_question = Word.objects.get(id=next_question_id)

        return Response(
            {
                "is_correct": is_correct,
                "correct_answer": correct_answer,
                "score": user_progress.score,
                "current_question_index": user_progress.current_question_index,
                "is_completed": False,
                "next_question": {
                    "id": next_question.id,
                    "question": next_question.japanese
                    if user_progress.mode == "en"
                    else next_question.english,
                    "question_number": user_progress.current_question_index + 1,
                    "total_questions": user_progress.total_questions,
                },
            }
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pause_quiz(request, progress_id):
    """
    クイズを中断

    POST /api/flashcard/progress/<id>/pause/
    """
    user_progress = get_object_or_404(
        UserProgress, id=progress_id, user=request.user, is_completed=False
    )

    user_progress.is_paused = True
    user_progress.save()

    return Response(
        {
            "message": "進行状況を保存しました",
            "progress": UserProgressSerializer(user_progress).data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def resume_quiz(request, progress_id):
    """
    クイズを再開

    POST /api/flashcard/progress/<id>/resume/
    """
    user_progress = get_object_or_404(
        UserProgress,
        id=progress_id,
        user=request.user,
        is_completed=False,
        is_paused=True,
    )

    user_progress.is_paused = False
    user_progress.save()

    # 現在の問題を取得
    questions = json.loads(user_progress.question_ids)
    current_question_id = questions[user_progress.current_question_index]
    current_question = Word.objects.get(id=current_question_id)

    return Response(
        {
            "progress": UserProgressSerializer(user_progress).data,
            "current_question": {
                "id": current_question.id,
                "question": current_question.japanese
                if user_progress.mode == "en"
                else current_question.english,
                "question_number": user_progress.current_question_index + 1,
                "total_questions": user_progress.total_questions,
            },
        }
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_progress(request, progress_id):
    """
    進行状況を削除

    DELETE /api/flashcard/progress/<id>/
    """
    user_progress = get_object_or_404(UserProgress, id=progress_id, user=request.user)

    user_progress.is_completed = True
    user_progress.is_paused = False
    user_progress.save()

    return Response(
        {"message": "進行状況を削除しました"}, status=status.HTTP_204_NO_CONTENT
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_statistics(request):
    """
    ユーザーの学習統計を取得

    GET /api/flashcard/statistics/
    """
    # 全ての正誤履歴を取得
    word_statuses = UserWordStatus.objects.filter(user=request.user)

    total_attempted = word_statuses.count()
    total_correct = word_statuses.filter(is_correct=True).count()
    total_incorrect = word_statuses.filter(is_correct=False).count()

    correct_rate = (
        round(total_correct / total_attempted * 100, 1) if total_attempted > 0 else 0.0
    )

    # レベル別統計
    by_level = []
    levels = Level.objects.all()
    for level in levels:
        level_statuses = word_statuses.filter(word__level=level)
        level_total = level_statuses.count()

        if level_total > 0:
            level_correct = level_statuses.filter(is_correct=True).count()
            level_rate = round(level_correct / level_total * 100, 1)

            by_level.append(
                {
                    "level_id": level.id,
                    "level_name": level.name,
                    "correct": level_correct,
                    "total": level_total,
                    "rate": level_rate,
                }
            )

    # モード別統計
    by_mode = {}
    for mode in ["en", "jp"]:
        mode_statuses = word_statuses.filter(mode=mode)
        mode_total = mode_statuses.count()

        if mode_total > 0:
            mode_correct = mode_statuses.filter(is_correct=True).count()
            mode_rate = round(mode_correct / mode_total * 100, 1)

            by_mode[mode] = {
                "correct": mode_correct,
                "total": mode_total,
                "rate": mode_rate,
            }

    # 最近の学習履歴
    recent_progress_qs = (
        UserProgress.objects.filter(user=request.user, is_completed=True)
        .select_related("level")
        .order_by("-completed_at")[:5]
    )

    recent_progress = []
    for progress in recent_progress_qs:
        recent_progress.append(
            {
                "id": progress.id,
                "level_name": progress.level.name,
                "mode": "English → Japanese"
                if progress.mode == "jp"
                else "Japanese → English",
                "score": progress.score,
                "total_questions": progress.total_questions,
                "correct_rate": round(
                    progress.score / progress.total_questions * 100, 1
                ),
                "completed_at": progress.completed_at,
            }
        )

    return Response(
        {
            "total_words_attempted": total_attempted,
            "total_correct": total_correct,
            "total_incorrect": total_incorrect,
            "correct_rate": correct_rate,
            "by_level": by_level,
            "by_mode": by_mode,
            "recent_progress": recent_progress,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_incorrect_words(request):
    """
    間違えた単語の一覧を取得

    GET /api/flashcard/incorrect-words/?mode=en&level=1
    """
    queryset = UserWordStatus.objects.filter(
        user=request.user, is_correct=False
    ).select_related("word", "word__level", "word__part_of_speech")

    # モードでフィルタ
    mode = request.query_params.get("mode")
    if mode:
        queryset = queryset.filter(mode=mode)

    # レベルでフィルタ
    level = request.query_params.get("level")
    if level:
        queryset = queryset.filter(word__level_id=level)

    serializer = UserWordStatusSerializer(queryset, many=True)
    return Response({"count": queryset.count(), "results": serializer.data})
