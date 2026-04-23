from django.urls import path
from .views import index_view, quiz_view

urlpatterns = [
    path('', index_view),
    path('quiz/', quiz_view),
]