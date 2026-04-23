from rest_framework import serializers
from .models import Quiz, Question, Choice, Result


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']


class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title']


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'questions']


class ResultSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = Result
        fields = [
            'id',
            'username',
            'quiz',
            'quiz_title',
            'score',
            'total_questions',
            'percentage',
            'feedback',
            'taken_at',
        ]