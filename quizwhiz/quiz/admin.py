from django.contrib import admin

from .models import Quiz, Question, Choice, Result


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    search_fields = ('text', 'quiz__title')
    inlines = [ChoiceInline]


class QuizAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


class ResultAdmin(admin.ModelAdmin):
    list_display = ('username', 'quiz', 'score', 'total_questions', 'percentage', 'taken_at')
    list_filter = ('quiz',)
    search_fields = ('username', 'quiz__title')
    readonly_fields = ('username', 'quiz', 'score', 'total_questions', 'percentage', 'feedback', 'taken_at')


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Result, ResultAdmin)
