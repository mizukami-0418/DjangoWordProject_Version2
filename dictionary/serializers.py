# dictionary/serializers.py

from rest_framework import serializers
from .models import Word, Level, PartOfSpeech


class PartOfSpeechSerializer(serializers.ModelSerializer):
    """品詞のシリアライザー"""

    class Meta:
        model = PartOfSpeech
        fields = ["id", "name"]


class LevelSerializer(serializers.ModelSerializer):
    """難易度のシリアライザー"""

    word_count = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = ["id", "name", "description", "word_count"]

    def get_word_count(self, obj):
        """このレベルの単語数を取得"""
        return obj.level.count()


class WordListSerializer(serializers.ModelSerializer):
    """単語一覧用のシリアライザー（軽量版）"""

    part_of_speech = serializers.StringRelatedField()
    level = serializers.StringRelatedField()

    class Meta:
        model = Word
        fields = ["id", "english", "japanese", "part_of_speech", "level"]


class WordDetailSerializer(serializers.ModelSerializer):
    """単語詳細用のシリアライザー（完全版）"""

    part_of_speech = PartOfSpeechSerializer(read_only=True)
    level = LevelSerializer(read_only=True)

    class Meta:
        model = Word
        fields = ["id", "english", "japanese", "part_of_speech", "phrase", "level"]


class WordSearchSerializer(serializers.Serializer):
    """単語検索用のシリアライザー"""

    query = serializers.CharField(
        required=True, max_length=255, help_text="検索クエリ（英語または日本語）"
    )
    level = serializers.IntegerField(
        required=False, help_text="難易度でフィルタ（オプション）"
    )
    part_of_speech = serializers.IntegerField(
        required=False, help_text="品詞でフィルタ（オプション）"
    )
    limit = serializers.IntegerField(
        required=False,
        default=50,
        max_value=100,
        help_text="最大結果数（デフォルト50、最大100）",
    )
