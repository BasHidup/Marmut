# urls.py

from django.urls import path
from chart.views import home_chart, detail_chart

app_name = 'chart'

urlpatterns = [
    path('', home_chart, name='home_chart'),
    path('<str:id>/', detail_chart, name='detail_chart'),
]