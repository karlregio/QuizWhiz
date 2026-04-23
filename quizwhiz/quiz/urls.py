from django.urls import path
from .views import *

urlpatterns = [
    # Pages
    path('', index_view),
    path('quiz/', quiz_view),
    path('result/', result_view),
    path('leaderboard/', leaderboard_view),

    # API
    path('api/quizzes/', quiz_list),
    path('api/quizzes/<int:pk>/', quiz_detail),
    path('api/quizzes/<int:pk>/submit/', submit_quiz),
    path('api/leaderboard/', leaderboard_api),
]