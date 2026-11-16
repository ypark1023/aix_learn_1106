import os
import json
import django

# 1. 본인 프로젝트의 settings 경로로 맞춰주세요 (예: 'screen1.settings')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "screen1.settings")
django.setup()

from screen.models import Screen, Actor  # 본인 앱 이름에 맞게 수정

with open("kobis_top100_movies.json", "r", encoding="utf-8") as f:
    movies = json.load(f)

for item in movies:
    # 개봉일에서 'YYYY-MM-DD' 형식만 추출
    raw_date = item.get("release_date", "")[:10]
    release_date = raw_date if len(raw_date) == 10 and raw_date[4] == "-" else None

    # 1) 먼저 Screen 객체 저장 (ManyToManyField인 actors는 여기서 제외)
    screen_obj, _ = Screen.objects.update_or_create(
        title=item["title"],
        defaults={
            "synopsis": item.get("synopsis", ""),
            "genre": item.get("genre", ""),
            "director": item.get("director", ""),
            "release_date": release_date,
            "poster": item.get("poster_url", ""),
        },
    )

    # 2) 배우 이름으로 Actor 객체를 찾거나 생성한 뒤 ManyToMany 연결
    actor_objs = []
    for actor_name in item.get("actors", []):
        name = actor_name.strip()
        if not name:
            continue
        actor_obj, _ = Actor.objects.get_or_create(name=name)
        actor_objs.append(actor_obj)

    screen_obj.actors.set(actor_objs)

print(f"DB 저장 완료! 영화 {Screen.objects.count()}편, 배우 {Actor.objects.count()}명")