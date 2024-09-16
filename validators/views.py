import json, inspect
from re import L
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import validators, Associated_validators
from user_apps.models import NewUser, user_app
from .utils import *
from prompts.models import prompts


class availablevalidators(View):
    
    def get(self, request):
        data = []
        try :
            validators_list = validators.objects.all()
            
            data = [ 
                    {
                        "name" : i.name,
                        "codename" : i.codename,
                        "descriptions" : i.descriptions,
                        "parameters" : i.parameters
                        }
                    for i in validators_list
                    ]
            
            return JsonResponse({'success': "The got all availablevalidators successfully", "data" : data}, status=201)
        except Exception as e :
            return JsonResponse({'error': f"Got an error : {e}", "data" : data}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class EditValidator(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        req_data= json.loads(request.body)
        req_keys = req_data.keys()
        if not "name" in req_keys or not "codename" in req_keys:
            return JsonResponse({'error': "there is not name of the app or the code name of the validator"}, status=400)
        
        if "codename" in req_keys :
            validator_obj = validators.objects.filter(codename = req_data['codename'])
        else :
            validator_obj = validators.objects.filter(codename = req_data['name'])
        
        if not validator_obj :
            return JsonResponse({'error': "could not find the validator"}, status=400)
            
        validator_obj = validator_obj.first()
        if "descriptions" in req_keys :
            validator_obj.descriptions = req_data['descriptions']
        
        if "parameters" in req_keys:
            validator_obj.parameters = req_data['parameters']
        
        if "new_codename" in req_keys:
            validator_obj.codename = req_data['new_codename']
            
        validator_obj.save()
        data = {
            "name" : validator_obj.name,
            "descriptions" : validator_obj.descriptions,
            "parameters" : validator_obj.parameters,
            "codename" : validator_obj.codename
        }
        
        return JsonResponse({'success': "successfully update the validator as the data below", "data" : data}, status=201)



@method_decorator(csrf_exempt, name='dispatch')
class CreateAssociatedValidator(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        req_data= json.loads(request.body)
        req_keys = req_data.keys()
        if not "apikey" in req_keys :
            return JsonResponse({'error': "there is not apikey for the Associated validator"}, status=400)
        
        if not "validators" in req_keys :
            return JsonResponse({'error': "there is not validator's list for the Associated validator creation"}, status=400)
        elif type(req_data['validators']) != list :
            return JsonResponse({'error': "validator must be in list types with contains json data of validators"}, status=400)
            
        user_app_obj = user_app.objects.filter(api_key=req_data['apikey'])
        if not user_app_obj :
            return JsonResponse({'error': "could not find the user app with apikey"}, status=400)
        user_app_obj = user_app_obj.first()
        
        for validator in req_data['validators'] : 
            if not "validator_codename" in validator.keys() :
                continue
            
            if not "parameters" in validator.keys() :
                parameters = {}
            else:
                parameters = validator['parameters']
                
            validator_obj = validators.objects.filter(codename = validator['validator_codename'])
            if not validator_obj:
                validator['created'] = False
                continue
                # return JsonResponse({'error': "could not find the validator"}, status=400)
        
            associated_validator_obj = Associated_validators.objects.filter(apikey = req_data['apikey'],validator = validator_obj.first())
            if associated_validator_obj :
                validator['created'] = False
                continue
                # return JsonResponse({'error': "already created the Associated validator with the given data"}, status=400)
            
            Associated_validators_obj = Associated_validators.objects.create(
                apikey = req_data['apikey'],
                parameters = parameters,
                validator = validator_obj.first(),
                user = user_app_obj.user,
                userapp = user_app_obj,
            )

            tmp_data = {
                "apikey" : Associated_validators_obj.apikey,
                "parameters" : Associated_validators_obj.parameters,
                "validator" : Associated_validators_obj.validator.name,
                "userapp" : Associated_validators_obj.userapp.app_name,
                "codename" : Associated_validators_obj.validator.codename
            }
            validator['created'] = True
            validator['data'] = tmp_data
        
        return JsonResponse({'success': "successfully created the Associated validator as the data given", "data" : req_data['validators']}, status=201)
        


@method_decorator(csrf_exempt, name='dispatch')
class EditAssociatedValidator(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        req_data= json.loads(request.body)
        req_keys = req_data.keys()
        if not "apikey" in req_keys :
            return JsonResponse({'error': "there is not apikey for the Associated validator"}, status=400)
        
        validator_obj = Associated_validators.objects.filter(apikey = req_data['apikey'])
        if not validator_obj :
            return JsonResponse({'error': "could not find the Associated validator"}, status=400)
            
        
        validator_obj = validator_obj.first()
        if "parameters" in req_keys:
            validator_obj.parameters = req_data['parameters']
        
            
        validator_obj.save()
        data = {
            "apikey" : validator_obj.apikey,
            "parameters" : validator_obj.parameters,
            "validator" : validator_obj.validator.name,
            "userapp" : validator_obj.userapp.app_name,
            "codename" : validator_obj.codename
        }
        
        return JsonResponse({'success': "successfully update the Associated validator as the data below", "data" : data}, status=201)
        

@method_decorator(csrf_exempt, name='dispatch')
class DeleteAssociatedValidator(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        req_data= json.loads(request.body)
        req_keys = req_data.keys()
        if not "apikey" in req_keys :
            return JsonResponse({'error': "there is not apikey for the Associated validator"}, status=400)
        
        validator_obj = Associated_validators.objects.filter(apikey = req_data['apikey'])
        if not validator_obj :
            return JsonResponse({'error': "could not find the Associated validator"}, status=400)
            
        validator_obj = validator_obj.first().delete()
        
        return JsonResponse({'success': "successfully delete the Associated validator as the data below"}, status=200)
        

@method_decorator(csrf_exempt, name='dispatch')
class validate(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        
        req_data= json.loads(request.body)
        req_keys = req_data.keys()
        if not "google_id" in req_keys or not "email" in req_keys or not "apikey" in req_keys or not "code_name" in req_keys :
            return JsonResponse({'error': "there is not google id or email or name of the app"}, status=400)
        
        user = NewUser.objects.filter(google_id = req_data['google_id'])
        if not user :
            user =  NewUser.objects.filter(email = req_data['email']) 
            if not user:
                return JsonResponse({'error': "No user found"}, status=400)
            
        user = user.first()
        apps_objects = user_app.objects.filter(user = user,api_key = req_data['apikey'] ) 
        if not apps_objects:
            return JsonResponse({'error': f"user doesnt have apps created named : {req_data['apikey']}"}, status=400)
        apps_object = apps_objects.first()
        
        validator_objects = validators.objects.filter(codename=req_data["code_name"])
        if not validator_objects:
            return JsonResponse({'error': f"user doesnt have any asoociated validator created"}, status=400)
        validator_object= validator_objects.first()
        validator_object.name
        
        asoociated_val_objects = Associated_validators.objects.filter(userapp=apps_object, validator=validator_object)
        if not asoociated_val_objects:
            return JsonResponse({'error': f"user doesnt have any asoociated validator created"}, status=400)
        asoociated_val_object= asoociated_val_objects.first()
        
        function_name = validator_object.name  # The name of the function as a string
        function_to_call = globals().get(function_name)
        if function_to_call is None:
            return JsonResponse({'error': f"Validator function '{function_name}' not found"}, status=400)

        args_to_pass = {}
        missing_param = []
        try:
            signature = inspect.signature(function_to_call)
            for param in signature.parameters.values(): 
                
                if param.name == "prompt":
                    args_to_pass[param.name] = req_data["prompt"]
                
                elif param.name in req_keys :
                    args_to_pass[param.name] = req_data[param.name]
                
                elif param.name in asoociated_val_object.parameters.keys():
                    args_to_pass[param.name] = asoociated_val_object.parameters[param.name]
                    
                elif param.default is not inspect.Parameter.empty:
                    args_to_pass[param.name] = param.default
                    
                else:
                    missing_param.append(param.name)
                    
                if missing_param :
                    return JsonResponse({'error': f"Missing required parameter: {missing_param}"}, status=400)
                
            try:
                result = function_to_call(**args_to_pass)
                prompts.objects.create(
                    app = apps_object,
                    user = user,
                    validate = result,
                    prompt = args_to_pass["prompt"]
                )
                return JsonResponse({'success': "successfully validate the prompt", "result" : result}, status=201)
                
            except Exception as e:
                return JsonResponse({'error': f"Validation failed: {str(e)}"}, status=400)
            
            
        except Exception as e:
            return JsonResponse({'error': f"Validation failed: {str(e)}"}, status=400)
