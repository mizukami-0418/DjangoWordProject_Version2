# dictionary/api_views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from .models import Word, Level, PartOfSpeech
from .serializers import (
    WordListSerializer,
    WordDetailSerializer,
    WordSearchSerializer,
    LevelSerializer,
    PartOfSpeechSerializer,
)


class WordListAPIView(generics.ListAPIView):
    """
    単語一覧を取得

    GET /api/dictionary/words/
    クエリパラメータ:
    - level: 難易度でフィルタ（例: ?level=1）
    - part_of_speech: 品詞でフィルタ（例: ?part_of_speech=1）
    - ordering: ソート順（例: ?ordering=english または ?ordering=-english）
    """

    serializer_class = WordListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Word.objects.select_related("part_of_speech", "level").all()

        # レベルでフィルタ
        level = self.request.query_params.get("level")
        if level:
            queryset = queryset.filter(level_id=level)

        # 品詞でフィルタ
        part_of_speech = self.request.query_params.get("part_of_speech")
        if part_of_speech:
            queryset = queryset.filter(part_of_speech_id=part_of_speech)

        # ソート
        ordering = self.request.query_params.get("ordering", "id")
        queryset = queryset.order_by(ordering)

        return queryset


class WordDetailAPIView(generics.RetrieveAPIView):
    """
    単語詳細を取得

    GET /api/dictionary/words/<id>/
    """

    serializer_class = WordDetailSerializer
    permission_classes = [IsAuthenticated]

    queryset = Word.objects.select_related("part_of_speech", "level").all()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def word_search(request):
    """
    単語検索

    GET /api/dictionary/search/?query=apple&level=1&limit=50

    クエリパラメータ:
    - query (必須): 検索クエリ（英語または日本語）
    - level (オプション): 難易度でフィルタ
    - part_of_speech (オプション): 品詞でフィルタ
    - limit (オプション): 最大結果数（デフォルト50、最大100）
    """
    # バリデーション
    serializer = WordSearchSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    query = data["query"]
    limit = data.get("limit", 50)

    # 検索クエリを構築
    # 英語は完全一致、日本語は部分一致
    search_filter = Q(english__iexact=query) | Q(japanese__icontains=query)

    queryset = Word.objects.filter(search_filter).select_related(
        "part_of_speech", "level"
    )

    # レベルでフィルタ
    if "level" in data:
        queryset = queryset.filter(level_id=data["level"])

    # 品詞でフィルタ
    if "part_of_speech" in data:
        queryset = queryset.filter(part_of_speech_id=data["part_of_speech"])

    # 結果を制限
    results = queryset[:limit]

    # シリアライズ
    result_serializer = WordListSerializer(results, many=True)

    return Response(
        {"query": query, "count": len(results), "results": result_serializer.data}
    )


class LevelListAPIView(generics.ListAPIView):
    """
    難易度一覧を取得

    GET /api/dictionary/levels/
    """

    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]


class PartOfSpeechListAPIView(generics.ListAPIView):
    """
    品詞一覧を取得

    GET /api/dictionary/parts-of-speech/
    """

    queryset = PartOfSpeech.objects.all()
    serializer_class = PartOfSpeechSerializer
    permission_classes = [IsAuthenticated]


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def word_random(request):
    """
    ランダムに単語を取得

    GET /api/dictionary/words/random/?count=10&level=1

    クエリパラメータ:
    - count (オプション): 取得する単語数（デフォルト10、最大50）
    - level (オプション): 難易度でフィルタ
    - part_of_speech (オプション): 品詞でフィルタ
    """
    count = int(request.query_params.get("count", 10))
    count = min(count, 50)  # 最大50件

    queryset = Word.objects.select_related("part_of_speech", "level").all()

    # レベルでフィルタ
    level = request.query_params.get("level")
    if level:
        queryset = queryset.filter(level_id=level)

    # 品詞でフィルタ
    part_of_speech = request.query_params.get("part_of_speech")
    if part_of_speech:
        queryset = queryset.filter(part_of_speech_id=part_of_speech)

    # ランダムに取得
    random_words = queryset.order_by("?")[:count]

    serializer = WordListSerializer(random_words, many=True)

    return Response({"count": len(random_words), "words": serializer.data})
