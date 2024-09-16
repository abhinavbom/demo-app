import json
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from google_auth.models import NewUser
from .models import user_app
from django.core import serializers
from validators.models import validators, Associated_validators
from rest_framework import status

@method_decorator(csrf_exempt, name='dispatch')
class create(View):
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        req_data= json.loads(request.body)
        if not ("google_id" and "email" and "app_name") in req_data.keys() :
            return JsonResponse({'error': "there is not google id or email or app's name"}, status=400)
        
        if not "validators" in req_data.keys() :
            return JsonResponse({'error': "not found validators's list"}, status=400)
        
        user = NewUser.objects.filter(google_id = req_data['google_id'],email = req_data['email'])
        if not user :
            return JsonResponse({'error': "No user found"}, status=400)
        
        user = user.first()
        if user_app.objects.filter(app_name = req_data['app_name'],user = user) :
            return JsonResponse({'error': "This app is already exists"}, status=400)
        
        user_app_obj = user_app.objects.create(app_name = req_data['app_name'],user = user)
        
        validators_list_data = []
        for validator in req_data['validators'] : 
            validator = {
                "validator_codename" : validator,
                "parameters" : {}
               }
            
            validator_obj = validators.objects.filter(codename = validator['validator_codename'])
            if not validator_obj:
                validator['created'] = False
                continue
        
            associated_validator_obj = Associated_validators.objects.filter(apikey = user_app_obj.api_key,validator = validator_obj.first())
            if associated_validator_obj :
                validator['created'] = False
                continue
            
            Associated_validators_obj = Associated_validators.objects.create(
                apikey = user_app_obj.api_key,
                parameters = validator["parameters"],
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
            validators_list_data.append(validator)
        
        data = {
            "app_name" : user_app_obj.app_name,
            "unique_id" : user_app_obj.unique_id,
            "api_key" : user_app_obj.api_key,
            "associated_validators" : validators_list_data
        }
        return JsonResponse({'success': "The app is created successfully", "data" : data}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class app_list(View):
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        user_app_list = []
        req_data= json.loads(request.body)
        if not ("google_id" or "email" ) in req_data.keys() :
            return JsonResponse({'error': "there is not google id or email"}, status=400)
        
        user = NewUser.objects.filter(google_id = req_data['google_id'])
        if not user :
            user =  NewUser.objects.filter(email = req_data['email']) 
            if not user:
                return JsonResponse({'error': "No user found"}, status=400)
        
        user = user.first()
        apps_objects = user_app.objects.filter(user = user) 
        if not apps_objects:
            return JsonResponse({'error': "user doesnt have any apps created"}, status=400)
        
        user_app_list = [ {"app_name" : i.app_name, "user_name" : i.user.name, "api_key" : i.api_key, "unique_id" : i.unique_id} for i in apps_objects]
        return JsonResponse({'success': "get the list of all apps successfully","app_lists" : user_app_list,'error': ''}, status=201)
    

@method_decorator(csrf_exempt, name='dispatch')
class app_details(View):
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        req_data= json.loads(request.body)
        
        if not "unique_id" in req_data.keys() :
            return JsonResponse({'error': "please provide unique_id"}, status=400)
        
        apps_objects = user_app.objects.filter(unique_id = req_data['unique_id'] ) 
        if not apps_objects:
            return JsonResponse({'error': f"Apikey is invalid"}, status=400)
        apps_objects = apps_objects.first()
        data = {}
        
        user_obj = apps_objects.user
        data['apikey'] = apps_objects.api_key
        data['app_name'] = apps_objects.app_name
        data['user_name'] = user_obj.name
        data['associated_validators'] = []
        
        validator_obj = Associated_validators.objects.filter(userapp = apps_objects)
        for validator in validator_obj :
            tmp = {}
            tmp['parameters'] = validator.parameters
            tmp['validator'] = {
                "name" : validator.validator.name,
                "codename" : validator.validator.codename,
                "descriptions" : validator.validator.descriptions
            }
            data['associated_validators'].append(tmp)
        
        
        return JsonResponse({'success': "get the details of apps successfully","data" : data,'error': ''}, status=200)
    


@method_decorator(csrf_exempt, name='dispatch')
class update_app(View):
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        """to update the app of user"""
        req_data= json.loads(request.body)
        
        if not "validators" in req_data.keys() :
            return JsonResponse({'error': "not found validators's list"}, status=400)
        
        if not "apikey" in req_data.keys() :
            return JsonResponse({'error': "not found apikey"}, status=400)
        
        apps_objects = user_app.objects.filter(api_key = req_data['apikey'] ) 
        if not apps_objects:
            return JsonResponse({'error': f"Apikey is invalid"}, status=400)
        
        apps_objects = apps_objects.first()
        
        if "app_name" in req_data.keys():
            apps_objects.app_name = req_data['app_name']
            apps_objects.save()
        
        user = apps_objects.user
            
        deleted_validators = req_data.get("del_validators",[])
        for validator in deleted_validators:
            validator_obj = validators.objects.filter(codename = validator['validator_codename'])
            if not validator_obj:
                validator['updated'] = False
                continue
            
            validator_obj = Associated_validators.objects.filter(apikey = apps_objects.api_key,validator = validator_obj.first())
            if not validator_obj:
                validator['updated'] = False
                continue
            validator_obj.first().delete()
        
        validators_list_data = []
        for validator in req_data['validators']:
            
            validator_obj = validators.objects.filter(codename = validator['validator_codename'])
            if not validator_obj:
                validator['updated'] = False
                continue
            validator_obj = validators.objects.filter(codename = validator['validator_codename']).first()
            associated_validator_obj = Associated_validators.objects.filter(apikey = apps_objects.api_key,validator = validator_obj)
            if not associated_validator_obj :
                associated_validator_obj = Associated_validators.objects.create(
                apikey = apps_objects.api_key,
                parameters = validator.get("parameters",{}),
                validator = validator_obj,
                user = user,
                userapp = apps_objects,
            )
            else :
                if "parameters" in validator.keys() :
                    associated_validator_obj.first().parameters = validator['parameters']
                    associated_validator_obj.first().save()
                    associated_validator_obj = associated_validator_obj.first()
                    
            tmp_data = {
                "apikey" : associated_validator_obj.apikey,
                "parameters" : associated_validator_obj.parameters,
                "validator" : associated_validator_obj.validator.name,
                "userapp" : associated_validator_obj.userapp.app_name,
                "codename" : associated_validator_obj.validator.codename
            }
            validator['data'] = tmp_data
            validators_list_data.append(validator)
        data = {
            "app_name" : apps_objects.app_name,
            "unique_id" : apps_objects.unique_id,
            "api_key" : apps_objects.api_key,
            "associated_validators" : validators_list_data
        }
        
        return JsonResponse({'success': "The app is updated successfully","data" : data,'error': ''}, status=status.HTTP_202_ACCEPTED)

@method_decorator(csrf_exempt, name='dispatch')
class delete_app(View):
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        """to delete the app of user"""

        user_app_list = []
        req_data= json.loads(request.body)
        req_keys = req_data.keys()
        if not "google_id" in req_keys or not "email" in req_keys or not "app_name" in req_keys :
            return JsonResponse({'error': "there is not google id or email or name of the app"}, status=400)
        
        user = NewUser.objects.filter(google_id = req_data['google_id'])
        if not user :
            user =  NewUser.objects.filter(email = req_data['email']) 
            if not user:
                return JsonResponse({'error': "No user found"}, status=400)
        
        user = user.first()
        apps_objects = user_app.objects.filter(user = user,app_name = req_data['app_name'] ) 
        if not apps_objects:
            return JsonResponse({'error': f"app not found named : {req_data['app_name']}"}, status=400)
        apps_objects.delete()
        
        return JsonResponse({'success': "The app is deleted successfully","app_lists" : user_app_list,'error': ''}, status=201)