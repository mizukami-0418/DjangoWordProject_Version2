# dictionary/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from dictionary.models import Word
from .serializers import WordSerializer


class WordListAPIView(APIView):
    def get(self, request):
        words = Word.objects.all()
        serializer = WordSerializer(words, many=True)
        return Response(serializer.data)
