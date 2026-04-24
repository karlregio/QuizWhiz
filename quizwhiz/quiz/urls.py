from django.urls import path
from .views import *

urlpatterns = [
    # Pages
    path('', index_view),
    path('quiz/', quiz_view),
    path('result/', result_view),
    path('leaderboard/', leaderboard_view),

    # ---------- PUBLIC API ----------
    path('api/quizzes/', quiz_list),
    path('api/quizzes/<int:pk>/', quiz_detail),
    path('api/quizzes/<int:pk>/submit/', submit_quiz),
    path('api/leaderboard/', leaderboard_api),

    # Categories & Topics
    path('api/categories/', category_list),
    path('api/categories/<int:pk>/', category_detail),
    path('api/categories/<int:pk>/subcategories/', category_subcategories),
    path('api/subcategories/<int:pk>/quizzes/', subcategory_quizzes),

    # ---------- ADMIN API ----------
    path('api/quizzes/create/', create_quiz),              # POST
    path('api/quizzes/<int:pk>/update/', update_quiz),     # PUT
    path('api/quizzes/<int:pk>/delete/', delete_quiz),     # DELETE
]