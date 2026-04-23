from django.db import models


class Quiz(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Result(models.Model):
    username = models.CharField(max_length=100)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.FloatField()
    feedback = models.CharField(max_length=255)
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.quiz.title}"