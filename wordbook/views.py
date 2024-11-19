from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'home.html')

# ERRORログ出力テスト用関数
def test_error(request):
    # ZeroDivisionErrorを発生させる
    result = 1 / 0
    return HttpResponse(f"The result is {result}")