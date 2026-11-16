from django.db import models

class Actor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Screen(models.Model):
    title = models.CharField(max_length=200)
    synopsis = models.TextField(blank=True)
    genre = models.CharField(max_length=100)
    director = models.CharField(max_length=100)
    actors = models.ManyToManyField(Actor, related_name='movies', blank=True) # 여러 배우 연결
    release_date = models.DateField(null=True, blank=True)
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)

    def __str__(self):
        return f'{self.title} ({self.release_date})'