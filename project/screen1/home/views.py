from django.shortcuts import render
from screen.models import Screen

# Create your views here.
def index(request):
    ranking_movies = Screen.objects.all()[:10]       # 1~10위
    # recommended_movies = Screen.objects.all()[10:15] # 11~15위 
    recommended_movies = Screen.objects.order_by('?')[:5] #.order_by('?')[:5] 로 랜덤 5개

    context = {
        "ranking_movies": ranking_movies,
        "recommended_movies": recommended_movies,
    }
    return render(request, "index.html", context)