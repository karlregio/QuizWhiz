from django.urls import path
from .views import (
    CategoryListAPIView,
    QuizListAPIView,
    QuizDetailAPIView,
    SubmitQuizAPIView,
    LeaderboardAPIView,
    AttemptHistoryAPIView,
)

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('quizzes/', QuizListAPIView.as_view(), name='quiz-list'),
    path('quizzes/<int:pk>/', QuizDetailAPIView.as_view(), name='quiz-detail'),
    path('quizzes/<int:pk>/submit/', SubmitQuizAPIView.as_view(), name='quiz-submit'),
    path('leaderboard/', LeaderboardAPIView.as_view(), name='leaderboard'),
    path('history/', AttemptHistoryAPIView.as_view(), name='attempt-history'),
]