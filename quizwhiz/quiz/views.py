from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
import random
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect


from .models import Category, Quiz, Result
from .serializers import (
    QuizListSerializer,
    ResultSerializer,
    CategorySerializer,
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

def history_view(request):
    return render(request, 'history.html')


# ---------- API VIEWS ----------

# - view quizzes
@api_view(['GET'])
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)

    questions = list(quiz.questions.all())
    random.shuffle(questions)

    question_data = []

    for q in questions:
        choices = list(q.choices.all())
        random.shuffle(choices)  # shuffle choices

        question_data.append({
            "id": q.id,
            "text": q.text,
            "choices": [
                {"id": c.id, "text": c.text}
                for c in choices
            ]
        })

    return Response({
        "id": quiz.id,
        "title": quiz.title,
        "questions": question_data
    })
    
@api_view(['GET'])
def result_detail(request, pk):
    result = get_object_or_404(Result, pk=pk)

    quiz = result.quiz
    answers_review = []

    for question in quiz.questions.all():
        correct = question.choices.filter(is_correct=True).first()

        # FIXED USER ANSWER LOGIC
        user_answer = "No answer"
        is_correct = False

        for a in result.answers:
            if a.get('question_id') == question.id:
                selected = question.choices.filter(id=a.get('choice_id')).first()

                if selected:
                    user_answer = selected.text
                    is_correct = correct and selected.id == correct.id
                break

        answers_review.append({
            "question": question.text,
            "user_answer": user_answer,
            "correct_answer": correct.text if correct else "",
            "is_correct": is_correct
        })

    return Response({
        "id": result.id,
        "score": result.score,
        "total_questions": result.total_questions,
        "percentage": result.percentage,
        "feedback": result.feedback,
        "time_taken": result.time_taken,
        "answers_review": answers_review
    })

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


# - submit quiz
@api_view(['POST'])
def submit_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)

    # Require login
    if not request.user.is_authenticated:
        return Response({'error': 'Login required.'}, status=401)

    username = request.user.username
    answers = request.data.get('answers', [])
    time_taken = request.data.get('time_taken', 0)

    score = 0
    total = quiz.questions.count()

    # collect answer review
    answers_review = []

    for ans in answers:
        try:
            question = quiz.questions.get(id=ans['question_id'])

            correct = question.choices.filter(is_correct=True).first()
            selected = question.choices.filter(id=ans['choice_id']).first()

            is_correct = correct and selected and correct.id == selected.id

            if is_correct:
                score += 1

            # store review data
            answers_review.append({
                "question": question.text,
                "correct_answer": correct.text if correct else "",
                "user_answer": selected.text if selected else "No answer",
                "is_correct": is_correct
            })

        except Exception as e:
            continue

    # Compute percentage
    percentage = (score / total) * 100 if total > 0 else 0

    # Feedback logic
    if percentage == 100:
        feedback = "Perfect score!"
    elif percentage >= 85:
        feedback = "Great job!"
    elif percentage >= 50:
        feedback = "Not bad."
    else:
        feedback = "Keep practicing."

    # Save result
    result = Result.objects.create(
        username=username,
        quiz=quiz,
        score=score,
        total_questions=total,
        percentage=percentage,
        feedback=feedback,
        time_taken=time_taken,
        answers=answers 
    )

    serializer = ResultSerializer(result)

    return Response({
        **serializer.data,
        "answers_review": answers_review
    })


# - leaderboard
@api_view(['GET'])
def leaderboard_api(request):
    category_id = request.GET.get('category')
    quiz_id = request.GET.get('quiz')

    results = Result.objects.select_related('quiz')

    # FILTERS
    if category_id:
        results = results.filter(quiz__category_id=category_id)

    if quiz_id:
        results = results.filter(quiz_id=quiz_id)

    # BEST SCORE PER USER PER QUIZ 
    best_map = {}

    for r in results:
        key = (r.username, r.quiz_id)

        if key not in best_map:
            best_map[key] = r
        else:
            existing = best_map[key]

            if (
                r.score > existing.score or
                (r.score == existing.score and r.percentage > existing.percentage) or
                (r.score == existing.score and r.percentage == existing.percentage and r.time_taken < existing.time_taken)
            ):
                best_map[key] = r

    best_results = list(best_map.values())

    best_results.sort(key=lambda r: (-r.score, -r.percentage, r.time_taken))

    data = [
        {
            "username": r.username,
            "quiz_title": r.quiz.title,
            "score": r.score,
            "total_questions": r.total_questions,
            "percentage": r.percentage,
            "feedback": r.feedback,
            "time_taken": r.time_taken
        }
        for r in best_results[:10]
    ]

    return Response(data)


# - list categories
@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()

    data = [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description
        }
        for c in categories
    ]

    return Response(data)

def category_page(request):
    return render(request, 'category.html')

# - category detail
@api_view(['GET'])
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serializer = CategorySerializer(category)
    return Response(serializer.data)

def get_global_average(user):
    results = Result.objects.filter(username=user.username)

    if not results.exists():
        return 0

    return sum(r.percentage for r in results) / len(results)


@api_view(['GET'])
def category_quizzes(request, pk):
    user = request.user

    quizzes = Quiz.objects.filter(category_id=pk)

    user_results = Result.objects.filter(
        username=user.username,
        quiz__category_id=pk
    )

    attempted_quiz_ids = set(user_results.values_list('quiz_id', flat=True))

    global_avg = get_global_average(user)

    data = []

    for q in quizzes:
        is_locked = False

        if q.difficulty == 'easy':
            is_locked = False

        elif q.difficulty == 'medium':
            easy_attempted = Quiz.objects.filter(
                category_id=pk,
                difficulty='easy',
                id__in=attempted_quiz_ids
            ).exists()

            is_locked = not easy_attempted

        elif q.difficulty == 'hard':
            medium_attempted = Quiz.objects.filter(
                category_id=pk,
                difficulty='medium',
                id__in=attempted_quiz_ids
            ).exists()

            is_locked = not (medium_attempted or global_avg >= 80)

        data.append({
            "id": q.id,
            "title": q.title,
            "difficulty": q.difficulty,
            "locked": is_locked
        })

    return Response(data)

@api_view(['GET'])
def user_history(request):
    if not request.user.is_authenticated:
        return Response([], status=401)

    results = Result.objects.filter(username=request.user.username)

    # SEARCH
    search = request.GET.get('search')
    if search:
        results = results.filter(quiz__title__icontains=search)

    # FILTER SA MIN PERCENTAGE
    min_pct = request.GET.get('min_pct')
    if min_pct:
        results = results.filter(percentage__gte=min_pct)

    # FILTER SA MAX PERCENTAGE
    max_pct = request.GET.get('max_pct')
    if max_pct:
        results = results.filter(percentage__lte=max_pct)

    # SORT 
    results = results.order_by('-taken_at')

    serializer = ResultSerializer(results, many=True)
    return Response(serializer.data)

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'Username already exists'
            })

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('/')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })

        login(request, user)
        return redirect('/')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def profile_view(request):
    return render(request, 'profile.html')


@api_view(['GET'])
def profile_api(request):
    username = request.user.username

    results = Result.objects.filter(username=username)

    total = results.count()

    best = max([r.percentage for r in results], default=0)

    avg = (
        sum([r.percentage for r in results]) / total
        if total else 0
    )

    total_time = sum([r.time_taken or 0 for r in results])

    recent = results.order_by('-id')[:5]

    return Response({
        "username": username,
        "total_quizzes": total,
        "best_score": best,
        "avg_score": avg,
        "total_time": total_time,
        "recent": [
            {
                "quiz": r.quiz.title,
                "score": r.score,
                "total": r.total_questions,
                "pct": r.percentage,
                "time": r.time_taken,
            } for r in recent
        ]
    })