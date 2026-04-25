from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from .models import Category, Quiz, Result, SubCategory
from .serializers import (
    QuizListSerializer,
    QuizDetailSerializer,
    ResultSerializer,
    CategorySerializer,
    SubCategorySerializer,
)


def index_view(request):
    return render(request, 'index.html')

def quiz_view(request):
    return render(request, 'quiz.html')

def result_view(request):
    return render(request, 'result.html')

def leaderboard_view(request):
    return render(request, 'leaderboard.html')

def category_view(request):
    return render(request, 'category.html')


# ---------- API VIEWS ----------

# PUBLIC - view quizzes
@api_view(['GET'])
def quiz_list(request):
    quizzes = Quiz.objects.all()
    serializer = QuizListSerializer(quizzes, many=True)
    return Response(serializer.data)


# PUBLIC - view quiz detail
@api_view(['GET'])
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    serializer = QuizDetailSerializer(quiz)
    return Response(serializer.data)


# ADMIN ONLY - create quiz
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_quiz(request):
    serializer = QuizListSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# ADMIN ONLY - update quiz
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    serializer = QuizListSerializer(quiz, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# ADMIN ONLY - delete quiz
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    quiz.delete()
    return Response({'message': 'Deleted'}, status=204)


# PUBLIC - submit quiz
@api_view(['POST'])
def submit_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)

    username = request.data.get('username', '').strip()
    answers = request.data.get('answers', [])
    time_taken = request.data.get('time_taken', 0)  # ✅ NEW

    if not username:
        return Response({'error': 'Username is required.'}, status=400)

    score = 0
    total = quiz.questions.count()

    for ans in answers:
        try:
            question = quiz.questions.get(id=ans['question_id'])
            correct = question.choices.filter(is_correct=True).first()

            if correct and correct.id == ans['choice_id']:
                score += 1
        except:
            continue

    percentage = (score / total) * 100 if total > 0 else 0

    if percentage >= 90:
        feedback = "Excellent performance!"
    elif percentage >= 75:
        feedback = "Good job!"
    elif percentage >= 50:
        feedback = "Fair attempt."
    else:
        feedback = "Needs improvement."

    result = Result.objects.create(
        username=username,
        quiz=quiz,
        score=score,
        total_questions=total,
        percentage=percentage,
        feedback=feedback,
        time_taken=time_taken,  # ✅ SAVE TIME
    )

    serializer = ResultSerializer(result)
    return Response(serializer.data)


# PUBLIC - leaderboard
@api_view(['GET'])
def leaderboard_api(request):
    results = Result.objects.select_related('quiz')\
        .order_by('-score', '-percentage', '-taken_at')[:10]

    serializer = ResultSerializer(results, many=True)
    return Response(serializer.data)


# PUBLIC - list categories
@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# PUBLIC - category detail
@api_view(['GET'])
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serializer = CategorySerializer(category)
    return Response(serializer.data)


# PUBLIC - subcategories by category
@api_view(['GET'])
def category_subcategories(request, pk):
    category = get_object_or_404(Category, pk=pk)
    subcategories = category.subcategories.all()
    serializer = SubCategorySerializer(subcategories, many=True)  # ✅ FIXED
    return Response(serializer.data)


# PUBLIC - quizzes by subcategory
@api_view(['GET'])
def subcategory_quizzes(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)  # ✅ FIXED
    quizzes = subcategory.quizzes.all()
    serializer = QuizListSerializer(quizzes, many=True)
    return Response(serializer.data)


# PUBLIC - quizzes by category
@api_view(['GET'])
def category_quizzes(request, pk):
    category = get_object_or_404(Category, pk=pk)
    quizzes = category.quizzes.all()

    serializer = QuizListSerializer(quizzes, many=True)
    return Response(serializer.data)