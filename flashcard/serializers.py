# flashcard/serializers.py

from rest_framework import serializers
from .models import UserProgress, UserWordStatus, UserReviewProgress
from dictionary.models import Word, Level
from dictionary.serializers import WordListSerializer, LevelSerializer


class UserWordStatusSerializer(serializers.ModelSerializer):
    """単語ごとの正誤履歴のシリアライザー"""

    word = WordListSerializer(read_only=True)
    word_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserWordStatus
        fields = [
            "id",
            "word",
            "word_id",
            "is_correct",
            "mode",
            "last_attempted_at",
        ]
        read_only_fields = ["id", "last_attempted_at"]


class UserProgressSerializer(serializers.ModelSerializer):
    """ユーザー進行状況のシリアライザー"""

    level = LevelSerializer(read_only=True)
    level_id = serializers.IntegerField(write_only=True)
    correct_rate = serializers.SerializerMethodField()

    class Meta:
        model = UserProgress
        fields = [
            "id",
            "level",
            "level_id",
            "mode",
            "score",
            "total_questions",
            "current_question_index",
            "question_ids",
            "completed_at",
            "is_completed",
            "is_paused",
            "correct_rate",
        ]
        read_only_fields = ["id", "completed_at"]

    def get_correct_rate(self, obj):
        """正答率を計算"""
        if obj.current_question_index > 0:
            return round(obj.score / obj.current_question_index * 100, 1)
        return 0.0


class UserProgressCreateSerializer(serializers.Serializer):
    """進行状況作成用のシリアライザー"""

    level_id = serializers.IntegerField(help_text="難易度ID")
    mode = serializers.ChoiceField(
        choices=["en", "jp"], help_text="モード（en: 英訳, jp: 和訳）"
    )
    quiz_mode = serializers.ChoiceField(
        choices=["normal", "test", "replay"],
        default="normal",
        help_text="クイズモード（normal: 通常, test: テスト100問, replay: 間違えた問題のみ）",
    )


class AnswerSubmitSerializer(serializers.Serializer):
    """回答送信用のシリアライザー"""

    progress_id = serializers.IntegerField(help_text="進行状況ID")
    answer = serializers.CharField(max_length=255, help_text="ユーザーの回答")


class UserReviewProgressSerializer(serializers.ModelSerializer):
    """復習進行状況のシリアライザー"""

    questions = WordListSerializer(many=True, read_only=True)
    correct_rate = serializers.SerializerMethodField()

    class Meta:
        model = UserReviewProgress
        fields = [
            "id",
            "mode",
            "current_question_index",
            "total_questions",
            "score",
            "is_completed",
            "is_paused",
            "created_at",
            "questions",
            "correct_rate",
        ]
        read_only_fields = ["id", "created_at"]

    def get_correct_rate(self, obj):
        """正答率を計算"""
        if obj.current_question_index > 0:
            return round(obj.score / obj.current_question_index * 100, 1)
        return 0.0


class StatisticsSerializer(serializers.Serializer):
    """統計情報のシリアライザー"""

    total_words_attempted = serializers.IntegerField(help_text="挑戦した単語数")
    total_correct = serializers.IntegerField(help_text="正解した単語数")
    total_incorrect = serializers.IntegerField(help_text="間違えた単語数")
    correct_rate = serializers.FloatField(help_text="正答率（%）")
    by_level = serializers.ListField(
        child=serializers.DictField(), help_text="レベル別統計"
    )
    by_mode = serializers.DictField(help_text="モード別統計")
    recent_progress = serializers.ListField(
        child=serializers.DictField(), help_text="最近の学習履歴（最新5件）"
    )
