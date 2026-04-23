from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Quiz, Result
from .serializers import QuizListSerializer, QuizDetailSerializer, ResultSerializer


# ---------- TEMPLATE VIEWS ----------

def index_view(request):
    return render(request, 'index.html')


def quiz_view(request):
    return render(request, 'quiz.html')


def result_view(request):
    return render(request, 'result.html')


def leaderboard_view(request):
    return render(request, 'leaderboard.html')


# ---------- API VIEWS ----------

@api_view(['GET'])
def quiz_list(request):
    quizzes = Quiz.objects.all()
    serializer = QuizListSerializer(quizzes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    serializer = QuizDetailSerializer(quiz)
    return Response(serializer.data)


@api_view(['POST'])
def submit_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)

    username = request.data.get('username', '').strip()
    answers = request.data.get('answers', [])

    if not username:
        return Response({'error': 'Username is required.'}, status=400)

    score = 0
    total = quiz.questions.count()

    for ans in answers:
        question_id = ans.get('question_id')
        choice_id = ans.get('choice_id')

        if question_id is None or choice_id is None:
            continue

        try:
            question = quiz.questions.get(id=question_id)
        except quiz.questions.model.DoesNotExist:
            continue

        correct_choice = question.choices.filter(is_correct=True).first()

        if correct_choice and correct_choice.id == choice_id:
            score += 1

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
    )

    serializer = ResultSerializer(result)
    return Response(serializer.data)


@api_view(['GET'])
def leaderboard_api(request):
    results = Result.objects.select_related('quiz')\
        .order_by('-score', '-percentage', '-taken_at')[:10]

    serializer = ResultSerializer(results, many=True)
    return Response(serializer.data)