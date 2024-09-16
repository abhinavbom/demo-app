from guardrails import Guard
from guardrails.hub import (
    RegexMatch, ToxicLanguage, MentionsDrugs,
    CompetitorCheck, ValidLength, ValidURL,
    ValidJson, ValidPython, ValidSQL,
    WebSanitization, ValidAddress, UnusualPrompt,
    SqlColumnPresence, ResponsivenessCheck, ReadingTime,
    QuotesPrice, OneLine, LowerCase,
    HasUrl, ExcludeSqlPredicates, EndpointIsReachable,
    SimilarToDocument, SaliencyCheck, RelevancyEvaluator,
    ProvenanceLLM, LowerCase, LogicCheck,
    GibberishText, ExtractedSummarySentencesMatch, DetectPII
)
import random





def match_regex(match_type = random.choice(["fullmatch","search"]), prompt : str = '', regex : str = '' ):
    """
    accept the prompt with parameters of regex in a string value
    return False :
        cond 1 :if not prompt or parameters
        cond 2 :if it is could not validate
    """
    
    if not prompt :
        return False
    
    if type(match_type) == list :
        if len(match_type) < 1 :
            match_type == "fullmatch"
    guard = Guard().use_many(
        RegexMatch(
            regex=regex,
            match_type = match_type
        )
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def toxic_language(prompt : str = '', validation_method : str = '', threshold : float = 0.5):
    if not prompt or not validation_method or not threshold :
        return False
    
    if validation_method not in ["sentence", "full"]:
        return False
    
    guard = Guard().use_many(
        ToxicLanguage(
            validation_method=validation_method,
            threshold=threshold
        )
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def mentions_drugs(prompt : str = ''):
    
    if not prompt :
        return False
    
    guard = Guard().use_many(
        MentionsDrugs()
    )

    validation = guard.validate(prompt)
    return validation.validation_passed
    
    
def competitor_check(prompt : str = '', competitors : list = []):
    if not prompt or not competitors :
        return False
    
    guard = Guard().use_many(
        CompetitorCheck(
            competitors=competitors
        )
    )
    
    validation = guard.validate(prompt)
    return validation.validation_passed
    
def valid_length(prompt : str = '', min : int = 0, max : int = 100 ):
    if not prompt or not min or not max :
        return False
    
    
    guard = Guard().use_many(
        ValidLength(
            min=min,
            max=max
        )
    )
    
    validation = guard.validate(prompt)
    return validation.validation_passed

def valid_url(prompt : str = ''):
    
    if not prompt :
        return False
    

    guard = Guard().use_many(
        ValidURL()
    )
    validation = guard.validate(prompt)
    return validation.validation_passed


def valid_json(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        ValidJson()
    )
    validation = guard.validate(prompt)
    return validation.validation_passed


def valid_python(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        ValidPython()
    )
    validation = guard.validate(prompt)
    return validation.validation_passed


def valid_sql(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        ValidSQL()
    )
    validation = guard.validate(prompt)
    return validation.validation_passed


def web_sanitization(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        WebSanitization()
    )
    validation = guard.validate(prompt)
    return validation.validation_passed

def valid_address(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        ValidAddress()
    )
    validation = guard.validate(prompt)
    return validation.validation_passed


def unusual_prompt(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        UnusualPrompt()
    )
    validation = guard.validate(prompt)
    return validation.validation_passed

def sql_column_presence(prompt : str = '', columns : list = []):
    if not prompt or not columns :
        return False
    
    guard = Guard().use_many(
        SqlColumnPresence(
            cols=columns
        )
    )
    
    validation = guard.validate(prompt)
    return validation.validation_passed

def responsiveness_check(prompt : str = '', columns : list = []):
    
    if not prompt :
        return False
    
    guard = Guard().use_many(
        ResponsivenessCheck(
            prompt=[prompt],
            llm_callable="gpt-3.5-turbo"
        )
    )
    validation = guard.validate(prompt)
    return validation.validation_passed


def reading_time(prompt : str = ''):
    
    if not prompt :
        return False
    
    guard = Guard().use_many(
        ReadingTime(
            reading_time=2
        )
    )
    validation = guard.validate(prompt)
    return validation.validation_passed

def quotes_price(prompt : str = ''):
    
    if not prompt :
        return False
    
    guard = Guard().use_many(
        QuotesPrice()
    )
    
    validation = guard.validate(prompt)
    return validation.validation_passed


def one_line(prompt : str = ''):
    
    if not prompt :
        return False
    
    guard = Guard().use_many(
        OneLine()
    )
    validation = guard.validate(prompt)
    return validation.validation_passed

def lower_case(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        LowerCase()
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def has_url(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        HasUrl()
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def exclude_sql_predicates(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        ExcludeSqlPredicates(
            predicates=["LIKE"]    # please check the parameters here in the lib.............. --------------------------------------------<<<<<<<<<<<<<<<<<<<<<<
        )
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def endpoint_is_reachable(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        EndpointIsReachable()
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def similar_to_document(prompt : str = '', document : str = '', threshold : float = 0.7):
    """
    Args:
        document (str): The document string to use for similarity check.
        threshold (float): The minimum cosine similarity to be considered similar.  Defaults to 0.7.
        model (str): The embedding model to use.  Defaults to "all-MiniLM-L6-v2" from SentenceTransformers.
        """
    if not prompt or not document or not threshold:
        return False

    guard = Guard().use_many(
        SimilarToDocument(
            document=document,
            threshold=threshold
        )
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def saliency_check(prompt : str = '', docs_dir : str = '', threshold : float = 0.25):
    """
    Args:

        docs_dir: Path to the directory containing the documents.
        llm_callable: Name of the LLM to use for extracting topics from the document.
            Default is `gpt-3.5-turbo` for LiteLLM.
        threshold: Minimum threshold for overlap between topics in document and summary.
            If the overlap is less than the threshold, the validation fails. Default is 0.25.
    """
    if not prompt or not docs_dir or not threshold:
        return False

    guard = Guard().use_many(
        SaliencyCheck(
            docs_dir=docs_dir,
            threshold=threshold
        )
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def relevancy_evaluator(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
            RelevancyEvaluator(
            llm_callable="gpt-3.5-turbo",
            on_fail=Exception
        )
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def provenance_llm(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        ProvenanceLLM()
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def profanity_free(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        LowerCase()
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def logic_check(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        LogicCheck(
        on_fail=Exception
        )
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def gibberish_text(prompt : str = ''):
    
    if not prompt :
        return False

    guard = Guard().use_many(
        GibberishText()
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def extracted_summary_sentences_match(prompt : str = '', filepaths : list = [], threshold : float = 0.7):
    """
    Args:

        threshold: The minimum cosine similarity to be considered similar. Default to 0.7.

    Other parameters: Metadata

        filepaths (List[str]): A list of strings that specifies the filepaths for any documents that should be used for asserting the summary's similarity.
        document_store (DocumentStoreBase, optional): The document store to use during validation. Defaults to EphemeralDocumentStore.
        vector_db (VectorDBBase, optional): A vector database to use for embeddings.  Defaults to Faiss.
        embedding_model (EmbeddingBase, optional): The embeddig model to use. Defaults to OpenAIEmbedding.
    """
    if not prompt or not threshold or not filepaths:
        return False

    guard = Guard().use_many(
        ExtractedSummarySentencesMatch(
        filepaths=filepaths,
        threshold=threshold
    )
    )

    validation = guard.validate(prompt)
    return validation.validation_passed

def detect_pii(prompt : str = ''):
    
    if not prompt :
        return False
    
    pii_entities = [
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "DOMAIN_NAME",
            "IP_ADDRESS",
            "DATE_TIME",
            "LOCATION",
            "PERSON",
            "URL",
        ]

    guard = Guard().use_many(
        DetectPII(
            pii_entities=pii_entities
        )
    )

    validation = guard.validate(prompt)
    return validation.validation_passed