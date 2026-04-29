from .import views
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

    # ---------- GET ALL DATA ----------
    path('api/all/', get_all_data),
    
    # Categories & Topics
    path('api/categories/', category_list),
    path('api/categories/create/', create_category),
    path('api/categories/<int:pk>/', category_detail),
    path('api/categories/<int:pk>/update/', update_category),
    path('api/categories/<int:pk>/delete/', delete_category),
    path('api/categories/<int:pk>/quizzes/', category_quizzes),
    path('category/', views.category_page, name='category_page'),

    # ---------- ADMIN API - Quiz CRUD ----------
    path('api/quizzes/', quiz_list),
    path('api/quizzes/create/', create_quiz),            
    path('api/quizzes/<int:pk>/update/', update_quiz),      
    path('api/quizzes/<int:pk>/delete/', delete_quiz),     

    # ---------- ADMIN API - Question CRUD ----------
    path('api/questions/', question_list),
    path('api/questions/create/', create_question),
    path('api/questions/<int:pk>/', question_detail),
    path('api/questions/<int:pk>/update/', update_question),
    path('api/questions/<int:pk>/delete/', delete_question),
    
    # ---------- ADMIN API - Choice CRUD ----------
    path('api/choices/', choice_list),
    path('api/choices/create/', create_choice),
    path('api/choices/<int:pk>/', choice_detail),
    path('api/choices/<int:pk>/update/', update_choice),
    path('api/choices/<int:pk>/delete/', delete_choice),

    # ---------- ADMIN API - Result CRUD ----------
    path('api/results/', result_list),
    path('api/results/<int:pk>/', result_detail),
    path('api/results/<int:pk>/delete/', delete_result),
]