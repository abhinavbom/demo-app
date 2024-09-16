from typing import List, Tuple
import json, inspect
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from rest_framework import status
from .models import prompts
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from google_auth.models import NewUser
from user_apps.models import user_app
from prompts.models import prompts
from validators.models import validators, Associated_validators
from guardrails import Guard, OnFailAction
from .utils import VALIDATORS

@method_decorator(csrf_exempt, name='dispatch')
class GetAllPrompts(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        req_data= json.loads(request.body)
        req_keys = req_data.keys()
        if not "google_id" in req_keys or not "email" in req_keys or not "app_name" in req_keys  :
            return JsonResponse({'error': "there is not google id or email or name of the app"}, status=400)
        
        user = NewUser.objects.filter(google_id = req_data['google_id'])
        if not user :
            user =  NewUser.objects.filter(email = req_data['email']) 
            if not user:
                return JsonResponse({'error': "No user found"}, status=400)
            
        user = user.first()
        apps_objects = user_app.objects.filter(user = user,app_name = req_data['app_name'] ) 
        if not apps_objects:
            return JsonResponse({'error': f"user doesnt have apps created named : {req_data['app_name']}"}, status=400)
        apps_object = apps_objects.first()
        data = [ { "prompt" : i.prompt, "validate" : i.validate, "created_at" : i.created_at} for i in prompts.objects.filter(app = apps_object, user = user)]
        
        return JsonResponse({'success': f"Got the all prompt from app name : {apps_object.app_name}", "data" : data}, status=200)
        
        
        
@method_decorator(csrf_exempt, name='dispatch')
class validate(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            req_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        # Validate API key and prompt presence
        apikey = req_data.get('apikey')
        prompt = req_data.get('prompt')
        guard_argument = req_data.get('guard_argument', {})  # Arguments for Guard and Validators
        validate_argument = req_data.get('validate_argument', {})  # Arguments for guard.validate()

        if not apikey:
            return JsonResponse({'error': 'API KEY is required'}, status=400)
        
        if not prompt:
            return JsonResponse({'error': 'Prompt is required'}, status=400)

        # Validate API key against the database
        user_app_obj = user_app.objects.filter(api_key=apikey).first()
        if not user_app_obj:
            return JsonResponse({'error': "Invalid API key"}, status=400)
        
        user_obj = user_app_obj.user

        # Fetch associated validators
        associated_val_objects = Associated_validators.objects.filter(userapp=user_app_obj)
        if not associated_val_objects:
            return JsonResponse({'error': "User does not have any associated validators created"}, status=400)

        # Prepare checks for validators
        checks = []
        for val in associated_val_objects:
            validator_object = val.validator
            tmp = {'type': validator_object.name}
            if validator_object.parameters:
                tmp['parameters'] = validator_object.parameters
                # Update parameters based on provided arguments
                for key, val in tmp['parameters'].items():
                    if key in guard_argument:
                        tmp['parameters'][key] = guard_argument[key]
            checks.append(tmp)

        # Initialize validator instances
        validators_instances = []

        for check in checks:
            check_type = check.get('type')
            parameters = check.get('parameters', {})
            validator_class = VALIDATORS.get(check_type)

            if not validator_class:
                return JsonResponse({'error': f'Unknown check type: {check_type}'}, status=400)

            # Create validator instance
            try:
                if parameters:
                    validator_instance = validator_class(**parameters, on_fail=OnFailAction.EXCEPTION)
                else:
                    validator_instance = validator_class(on_fail=OnFailAction.EXCEPTION)
                
                validators_instances.append(validator_instance)
            except TypeError as e:
                return JsonResponse({'error': f'Error initializing validator {check_type}: {str(e)}'}, status=400)

        # Initialize Guard with validators
        guard = Guard().use_many(*validators_instances)

        # Validate the prompt using Guard
        try:
            if validate_argument :
                local_context = {}
                breakpoint()
                # Construct validate_argument dynamically and pass it to guard.validate()
                validate_kwargs = validate_argument.get('metadata', {}) if 'metadata' in validate_argument else {}
                if "query_function" in validate_kwargs.keys():
                    imports = validate_argument['imports']
                    for imp in imports: exec(imp, {}, local_context)
                    function_code = validate_kwargs['query_function']
                    exec(function_code,{},local_context)  
                    query_function = local_context.get('query_function')  
                    validate_kwargs['query_function'] = query_function
                result = guard.validate(prompt,metadata= validate_kwargs)
            else:
                result = guard.validate(prompt)
            # Save validation result to the database
            prompts.objects.create(
                app=user_app_obj,
                user=user_obj,
                validate=result.validation_passed,
                prompt=prompt
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        return JsonResponse({'message': 'Prompt validated successfully!', "result": result.validation_passed}, status=200)
        
        
# @method_decorator(csrf_exempt, name='dispatch')
# class validate(View):
#     @method_decorator(csrf_exempt)
#     def post(self, request):
        
#         req_data= json.loads(request.body)
#         req_keys = req_data.keys()
#         if not "prompt" in req_keys  :
#             return JsonResponse({'error': "prompt is not provided"}, status=400)
        
#         if not "apikey" in req_keys  :
#             return JsonResponse({'error': "api key is not provided"}, status=400)
        
        
#         user_app_obj = user_app.objects.filter(api_key= req_data['apikey'])
#         if not user_app_obj :
#             return JsonResponse({'error': "invalid api key"}, status=400)
#         user_app_obj = user_app_obj.first()
#         user_obj = user_app_obj.user
        
#         asoociated_val_objects = Associated_validators.objects.filter(userapp=user_app_obj)
#         if not asoociated_val_objects:
#             return JsonResponse({'error': f"user does not have any asoociated validator created"}, status=400)

#         data = {}
#         validate_data = {}
#         for val in asoociated_val_objects :
#             tmp = {}
#             validate_data['error'] = []

#             validator_objects = val.validator
#             function_name = validator_objects.name 
#             function_to_call = globals().get(function_name)
#             if function_to_call is None:
#                 validate_data['error'].append( f"Validator '{function_name}' not found")
                
#             args_to_pass = {}
#             missing_param = []
#             try:
#                 signature = inspect.signature(function_to_call)
#                 for param in signature.parameters.values(): 
                    
#                     if param.name == "prompt":
#                         args_to_pass[param.name] = req_data["prompt"]
                    
#                     elif param.name in req_keys :
#                         args_to_pass[param.name] = req_data[param.name]
                    
#                     elif param.name in asoociated_val_objects.first().parameters.keys():
#                         args_to_pass[param.name] = asoociated_val_objects.first().parameters[param.name]
                        
#                     elif param.default is not inspect.Parameter.empty:
#                         args_to_pass[param.name] = param.default
                        
#                     else:
#                         missing_param.append(param.name)
                        
#                     if missing_param :
#                         validate_data['error'].append(f"Missing required parameter: {missing_param}")
                    
#                 try:
#                     result = function_to_call(**args_to_pass)
#                     prompts.objects.create(
#                         app = user_app_obj,
#                         user = user_obj,
#                         validate = result,
#                         prompt = args_to_pass["prompt"]
#                     )
#                     tmp['result'] = result
#                     tmp['prompt'] = req_data["prompt"]
                    
#                 except Exception as e:
#                     validate_data['error'].append(f"Validation failed: {str(e)}")
                
#             except Exception as e:
#                 validate_data['error'].append(f"Validation failed: {str(e)}")
#             tmp['erros'] = validate_data['error']
#             data[validator_objects.name ] = tmp
            
            
#         return JsonResponse({'data': data}, status=status.HTTP_200_OK)
        
        
        
  # checks = [
        # {
        #     "type": "regex_match",
        #     "parameters": {
        #         "regex": "\\(?\\d{3}\\)?-? *\\d{3}-? *-?\\d{4}"
        #     }
        # },
        # {
        #     "type": "toxic_language",
        #     "parameters": {}
        # },
        #         {
        #     "type": "mentions_drugs",
        #     "parameters": {}
        # }
        # ]