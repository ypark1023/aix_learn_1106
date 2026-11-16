from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Screen

def slist(request):
    qs = Screen.objects.prefetch_related("actors").all()[:10]

    movies_data = []
    for idx, m in enumerate(qs, start=1):
        movies_data.append({
            "id": m.id,
            "rank": idx,
            "title": m.title,
            "synopsis": m.synopsis or "등록된 줄거리가 없습니다.",
            "year": m.release_date.year if m.release_date else "-",
            "genre": m.genre or "영화",
            "director": m.director or "-",
            "actors": [a.name for a in m.actors.all()[:3]],
            "audience": f"역대 {idx}위",
            "palette": ["#0D0D1A", "#2400FF", "#00F0FF"],
            "posterUrl": str(m.poster) if m.poster else "",
        })

    return render(request, "slist.html", {"movies_data": movies_data})