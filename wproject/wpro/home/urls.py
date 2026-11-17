from django.urls import path,include
from . import views

app_name = ''
urlpatterns = [
    path('', views.index, name='index'),
    # path('predict_weight/', views.predict_weight, name='predict_weight'),
    path('ajax_data/', views.ajax_data, name='ajax_data'),

]