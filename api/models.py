from django.db import models


class Survey(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    current_version = models.OneToOneField(
        to='SurveyVersion',
        on_delete=models.SET_NULL,
        null=True
    )


class SurveyVersion(models.Model):
    base = models.ForeignKey(
        to='Survey',
        related_name='versions',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(verbose_name='created at', auto_now_add=True)


class Question(models.Model):

    class QuestionTypes(models.TextChoices):
        INPUT_VALUE = "I", "input_value"
        SINGLE_CHOICE = "S", "single_choice"
        MULTIPLE_CHOICE = "M", "multiple_choice"

    survey_version = models.ForeignKey(
        SurveyVersion, related_name="questions", on_delete=models.CASCADE
    )
    question_text = models.CharField(max_length=1024)
    question_type = models.CharField(
        max_length=1,
        choices=QuestionTypes.choices,
        default=QuestionTypes.INPUT_VALUE.value,
    )
    previous_question = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="previous question",
    )


class Option(models.Model):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    option_text = models.CharField(max_length=128, default='Enter some value')


class Answer(models.Model):
    customer_id = models.IntegerField(verbose_name="customer")
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    answer_value = models.CharField(max_length=128, blank=True, null=True)


class CustomerSurveyAttempt(models.Model):
    customer_id = models.IntegerField(verbose_name="customer")
    survey = models.ForeignKey(Survey, related_name="attempts", on_delete=models.CASCADE)
    survey_version = models.ForeignKey(SurveyVersion, on_delete=models.CASCADE, null=True)
    current_question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.SET_NULL)
    attempts_count = models.PositiveSmallIntegerField(default=0)
