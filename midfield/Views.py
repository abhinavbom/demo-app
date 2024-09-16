from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from guardrails import Guard, OnFailAction
from guardrails.hub import (
    ArizeDatasetEmbeddings, CorrectLanguage, DetectPromptInjection, ExtractiveSummary, NSFWText, ProvenanceEmbeddings, QARelevanceLLMEval,
    RestrictToTopic, SecretsPresent, SimilarToPreviousValues, WikiProvenance,
    CsvMatch, EndsWith, FinancialTone, LLMCritic, MentionsDrugs, PolitenessCheck,
    ReadingLevel, RedundantSentences, ResponseEvaluator, SensitiveTopic, TwoWords,
    UpperCase, ValidChoices, ValidLength, ValidPython, ValidSQL, WebSanitization,
    ValidURL, ValidRange, ValidOpenApiSpec, ValidJson, ValidAddress, UnusualPrompt,
    SqlColumnPresence, ResponsivenessCheck, RegexMatch, ReadingTime, QuotesPrice,
    OneLine, LowerCase, HasUrl, ExcludeSqlPredicates, EndpointIsReachable, ToxicLanguage, SimilarToDocument, SaliencyCheck, RelevancyEvaluator,
    ProvenanceLLM, ProfanityFree, LogicCheck, GibberishText, ExtractedSummarySentencesMatch,
    DetectPII, CompetitorCheck
)

class PromptView(APIView):
    def post(self, request, *args, **kwargs):
        apikey = request.data.get('apikey')
        prompt = request.data.get('prompt')

        checks = [
        # {
        #     "type": "regex_match",
        #     "parameters": {
        #         "regex": "\\(?\\d{3}\\)?-? *\\d{3}-? *-?\\d{4}"
        #     }
        # },
        {
            "type": "toxic_language",
            "parameters": {}
        },
                {
            "type": "mentions_drugs",
            "parameters": {}
        }
    ]

        if not apikey:
            return Response({'error': 'API KEY is required'}, status=status.HTTP_400_BAD_REQUEST)
        if apikey != 'test-key':
            return Response({'error': 'Provided API KEY is invalid'}, status=status.HTTP_400_BAD_REQUEST)

        if not prompt:
            return Response({'error': 'Prompt is required'}, status=status.HTTP_400_BAD_REQUEST)


        # Map of check types to validator classes
        validators = {
            'arize_dataset_embeddings': ArizeDatasetEmbeddings,
            'correct_language': CorrectLanguage,
            'detect_prompt_injection': DetectPromptInjection,
            'extractive_summary': ExtractiveSummary,
            'nsfw_text': NSFWText,
            'provenance_embeddings': ProvenanceEmbeddings,
            'qa_relevance_llm_eval': QARelevanceLLMEval,
            'restrict_to_topic': RestrictToTopic,
            'secrets_present': SecretsPresent,
            'similar_to_previous_values': SimilarToPreviousValues,
            'wiki_provenance': WikiProvenance,
            'csv_match': CsvMatch,
            'ends_with': EndsWith,
            'financial_tone': FinancialTone,
            'llm_critic': LLMCritic,
            'mentions_drugs': MentionsDrugs,
            'politeness_check': PolitenessCheck,
            'reading_level': ReadingLevel,
            'redundant_sentences': RedundantSentences,
            'response_evaluator': ResponseEvaluator,
            'sensitive_topic': SensitiveTopic,
            'two_words': TwoWords,
            'upper_case': UpperCase,
            'valid_choices': ValidChoices,
            'valid_length': ValidLength,
            'valid_python': ValidPython,
            'valid_sql': ValidSQL,
            'web_sanitization': WebSanitization,
            'valid_url': ValidURL,
            'valid_range': ValidRange,
            'valid_openapi_spec': ValidOpenApiSpec,
            'valid_json': ValidJson,
            'valid_address': ValidAddress,
            'unusual_prompt': UnusualPrompt,
            'sql_column_presence': SqlColumnPresence,
            'responsiveness_check': ResponsivenessCheck,
            'regex_match': RegexMatch,
            'reading_time': ReadingTime,
            'quotes_price': QuotesPrice,
            'one_line': OneLine,
            'lower_case': LowerCase,
            'has_url': HasUrl,
            'exclude_sql_predicates': ExcludeSqlPredicates,
            'endpoint_is_reachable': EndpointIsReachable,
            'toxic_language': ToxicLanguage,
            'similar_to_document': SimilarToDocument,
            'saliency_check': SaliencyCheck,
            'relevancy_evaluator': RelevancyEvaluator,
            'provenance_llm': ProvenanceLLM,
            'profanity_free': ProfanityFree,
            'logic_check': LogicCheck,
            'gibberish_text': GibberishText,
            'extracted_summary_sentences_match': ExtractedSummarySentencesMatch,
            'detect_pii': DetectPII,
            'competitor_check': CompetitorCheck,
        }

        validators_instances = []

        for check in checks:
            check_type = check.get('type')
            parameters = check.get('parameters', {})
            validator_class = validators.get(check_type)
            if not validator_class:
                return Response({'error': f'Unknown check type: {check_type}'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                validator_instance = validator_class(**parameters, on_fail=OnFailAction.EXCEPTION)
                validators_instances.append(validator_instance)
            except TypeError as e:
                return Response({'error': f'Error initializing validator {check_type}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        guard = Guard().use_many(*validators_instances)

        try:
            guard.validate(prompt)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Prompt validated successfully!'}, status=status.HTTP_200_OK)
