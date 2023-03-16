from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import *
from .serializers import *


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    def retrieve(self, request, pk=None, version_id=None):
        if version_id:
            survey = self.get_object()
            survey.current_version_id = version_id
            serializer = self.get_serializer(survey)
            return Response(serializer.data)
        return super().retrieve(request, pk)

    @action(detail=True, methods=['get'])
    def start(self, request, pk=None):
        """
        Start survey for customer
        """
        customer_survey_attempt, created = CustomerSurveyAttempt.objects.get_or_create(
            customer_id=self.request.user.id,
            survey_id=pk
        )
        # Get parent survey question
        parent_question = Question.objects.filter(
            survey_version__base_id=pk,
            previous_question_id=None
        ).first()
        
        if created:
            survey = Survey.objects.get(pk=pk)
            # Set parent survey question to current 
            customer_survey_attempt.current_question = parent_question
            customer_survey_attempt.survey_version = survey.current_version
            customer_survey_attempt.attempts_count = 1
        
        # Check next survey question exists
        next_question_exists = Question.objects.filter(
            survey_version__base_id=pk,
            previous_question=customer_survey_attempt.current_question
        ).exists()

        if not next_question_exists:
            # Another survey attempt for customer => increment counter
            customer_survey_attempt.attempts_count += 1
            customer_survey_attempt.current_question = parent_question
            customer_survey_attempt.survey_version = survey.current_version
        
        customer_survey_attempt.save()
        
        return Response(CustomerSurveyAttemptSerializer(customer_survey_attempt).data)
    
    @action(detail=True, methods=['post'])
    def question_answer(self, request, pk=None):
        serializer = AnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer = Answer.objects.create(
            customer_id=self.request.user.id,
            question_id=request.data['question_id'],
            option_id=request.data['option_id'],
            answer_value=request.data['answer_value'],
        )
        # Find next question
        next_question = Question.objects.filter(previous_question_id=answer.question_id).first()
        next_question_id = next_question.pk if next_question else None
        answer.next_question_id = next_question_id
        
        # Update current question at attempt
        survey = Survey.objects.get(pk=pk)
        CustomerSurveyAttempt.objects.filter(
            customer_id=self.request.user.id,
            survey_version=survey.current_version,
            survey_id=pk
        ).update(
            current_question_id=next_question_id
        )

        return Response(AnswerSerializer(answer).data)
