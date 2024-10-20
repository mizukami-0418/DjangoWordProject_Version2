# error/views.py

from django.shortcuts import render

# Create your views here.
# exceptionを使わない場合でも引数として受け取る必要がある
def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)
