from django.shortcuts import render, get_object_or_404
from .models import Quiz, Result

def index_view(request):
    quizzes = Quiz.objects.all()
    return render(request, 'index.html', {'quizzes': quizzes})


def quiz_view(request):
    quiz_id = request.GET.get('id')
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        score = 0
        total = quiz.questions.count()

        for question in quiz.questions.all():
            selected = request.POST.get(f'q{question.id}')
            correct = question.choices.filter(is_correct=True).first()

            if selected and correct and int(selected) == correct.id:
                score += 1

        percentage = (score / total) * 100 if total > 0 else 0

        if percentage >= 90:
            feedback = "Excellent!"
        elif percentage >= 75:
            feedback = "Good job!"
        elif percentage >= 50:
            feedback = "Fair attempt"
        else:
            feedback = "Try again"

        Result.objects.create(
            username=username,
            quiz=quiz,
            score=score,
            total_questions=total,
            percentage=percentage,
            feedback=feedback
        )

        return render(request, 'result.html', {
            'score': score,
            'total': total,
            'percentage': percentage,
            'feedback': feedback
        })

    return render(request, 'quiz.html', {'quiz': quiz})