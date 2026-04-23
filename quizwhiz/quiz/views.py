from django.shortcuts import render

from decimal import Decimal

from django.db.models import Max
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Quiz, Result
from .serializers import (
    CategorySerializer,
    QuizListSerializer,
    QuizDetailSerializer,
    ResultSerializer,
)

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer


class QuizListAPIView(generics.ListAPIView):
    serializer_class = QuizListSerializer

    def get_queryset(self):
        queryset = Quiz.objects.select_related('category').all().order_by('-created_at')
        search = self.request.query_params.get('search')
        category_id = self.request.query_params.get('category')

        if search:
            queryset = queryset.filter(title__icontains=search)

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset


class QuizDetailAPIView(generics.RetrieveAPIView):
    queryset = Quiz.objects.select_related('category').prefetch_related('questions__choices')
    serializer_class = QuizDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        quiz = self.get_object()
        serializer = self.get_serializer(quiz)
        data = serializer.data

        random.shuffle(data['questions'])
        return Response(data)
    
class SubmitQuizAPIView(APIView):
    def post(self, request, pk):
        username = request.data.get('username')
        answers = request.data.get('answers', [])

        if not username:
            return Response({'error': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)

        quiz = Quiz.objects.prefetch_related('questions__choices').filter(pk=pk).first()
        if not quiz:
            return Response({'error': 'Quiz not found.'}, status=status.HTTP_404_NOT_FOUND)

        total_questions = quiz.questions.count()
        score = 0
        detailed_results = []

        submitted_answers = {item['question_id']: item['choice_id'] for item in answers if 'question_id' in item and 'choice_id' in item}

        for question in quiz.questions.all():
            correct_choice = question.choices.filter(is_correct=True).first()
            selected_choice_id = submitted_answers.get(question.id)
            is_correct = correct_choice and selected_choice_id == correct_choice.id

            if is_correct:
                score += 1

            detailed_results.append({
                'question_id': question.id,
                'question_text': question.text,
                'selected_choice_id': selected_choice_id,
                'correct_choice_id': correct_choice.id if correct_choice else None,
                'is_correct': bool(is_correct),
            })
        percentage = Decimal((score / total_questions) * 100 if total_questions > 0 else 0).quantize(Decimal('0.01'))

        if percentage >= 90:
            feedback = 'Excellent performance!'
        elif percentage >= 75:
            feedback = 'Good job!'
        elif percentage >= 50:
            feedback = 'Fair attempt. Keep practicing.'
        else:
            feedback = 'Needs improvement. Try again.'

        result = Result.objects.create(
            username=username,
            quiz=quiz,
            score=score,
            total_questions=total_questions,
            percentage=percentage,
            feedback=feedback,
        )
        
        return Response(
            {
                'message': 'Quiz submitted successfully.',
                'result': ResultSerializer(result).data,
                'answer_review': detailed_results,
            },
            status=status.HTTP_201_CREATED,
        )
        
class LeaderboardAPIView(APIView):
    def get(self, request):
        quiz_id = request.query_params.get('quiz')
        queryset = Result.objects.select_related('quiz').all()

        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)

        queryset = queryset.order_by('-score', '-percentage', 'taken_at')[:10]

        data = []
        for index, item in enumerate(queryset, start=1):
            data.append({
                'rank': index,
                'username': item.username,
                'quiz': item.quiz.title,
                'score': item.score,
                'total_questions': item.total_questions,
                'percentage': item.percentage,
                'taken_at': item.taken_at,
            })

        return Response(data)
    
class AttemptHistoryAPIView(generics.ListAPIView):
    serializer_class = ResultSerializer

    def get_queryset(self):
        username = self.request.query_params.get('username')
        queryset = Result.objects.select_related('quiz').all().order_by('-taken_at')

        if username:
            queryset = queryset.filter(username=username)

        return queryset
