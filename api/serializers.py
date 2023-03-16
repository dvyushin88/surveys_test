from rest_framework import serializers

from .models import *


class OptionSerializer(serializers.ModelSerializer):
    option_text = serializers.CharField(max_length=128)
    
    class Meta:
        model = Option
        fields = ('id', 'question_id', 'option_text')
        read_only_fields = ('id', )


class QuestionSerializer(serializers.ModelSerializer):
    question_type = serializers.ChoiceField(
        choices=Question.QuestionTypes.choices, default=Question.QuestionTypes.INPUT_VALUE
    )
    question_text = serializers.CharField(max_length=1024)
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ('id', 'survey_version_id', 'question_text', 'question_type', 'previous_question_id', 'options')
        read_only_fields = ('id', )


class SurveySerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=128)
    description = serializers.CharField(max_length=1024)
    questions = QuestionSerializer(source='current_version.questions', many=True, required=False)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'current_version_id', 'questions')
        read_only_fields = ('id', )
    
    def create_options(self, question, options):
        Option.objects.bulk_create([
            Option(question=question, **o) for o in options
        ])
    
    def create_questions(self, survey_version, questions):
        previous_question_id = None

        for q in questions:
            options = q.pop('options', [])
            q.pop('previous_question_id', None)
            question = Question.objects.create(
                survey_version=survey_version,
                previous_question_id=previous_question_id,
                **q
            )
            previous_question_id = question.pk
            self.create_options(question, options)

    def create(self, validated_data):
        current_version = validated_data.pop('current_version')
        survey = Survey.objects.create(**validated_data)
        survey_version = SurveyVersion.objects.create(base=survey)
        survey.current_version = survey_version
        survey.save()
        self.create_questions(survey_version, current_version['questions'])
        
        return survey

    def update(self, instance, validated_data):
        # Every update bump Survey version and creates new questions and options
        current_version = validated_data.pop('current_version')
        survey_version = SurveyVersion.objects.create(base=instance)
        self.create_questions(survey_version, current_version['questions'])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        
        instance.current_version = survey_version
        instance.save()
        
        return instance


class AnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    option_id = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all())
    answer_value = serializers.CharField(max_length=128, required=False)
    next_question_id = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all(), required=False)

    class Meta:
        model = Answer
        fields = ('id', 'customer_id', 'question_id', 'option_id', 'answer_value', 'next_question_id')
        read_only_fields = ('id', 'customer_id')


class CustomerSurveyAttemptSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerSurveyAttempt
        fields = ('customer_id', 'current_question_id', 'attempts_count', 'survey_id', 'survey_version_id')
        read_only_fields = ('customer_id', 'current_question_id', 'survey_version_id')
