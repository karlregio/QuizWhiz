from django.urls import path
from .views import *

urlpatterns = [
    # Pages
    path('', index_view),
    path('quiz/', quiz_view),
    path('result/', result_view),
    path('leaderboard/', leaderboard_view),
    path('history/', history_view),
    # ---------- Auth Routes ----------
    path('login/', login_view),
    path('register/', register_view),
    path('logout/', logout_view),

    # ---------- PUBLIC API ----------
    path('api/quizzes/<int:pk>/', quiz_detail),
    path('api/quizzes/<int:pk>/submit/', submit_quiz),
    path('api/leaderboard/', leaderboard_api),
    
    # ---------- USER API ----------
    path('api/my-results/', user_history),
    path('api/results/<int:pk>/', result_detail),
    
    # ---------- PROFILE API ----------
    path('profile/', profile_view),
    path('api/profile/', profile_api),

    # Categories & Topics
    path('api/categories/', category_list),
    path('api/categories/<int:pk>/', category_detail),
    path('api/categories/<int:pk>/quizzes/', category_quizzes),


    # ---------- ADMIN API ----------
    path('api/quizzes/create/', create_quiz),              # POST
    path('api/quizzes/<int:pk>/update/', update_quiz),     # PUT
    path('api/quizzes/<int:pk>/delete/', delete_quiz),     # DELETE
    
]