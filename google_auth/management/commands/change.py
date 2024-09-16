from django.core.management.base import BaseCommand
from validators.models import validators

class Command(BaseCommand):

        def handle(self, *args, **options):
            
            for val in validators.objects.all():
                metadata = val.parameters['metadata']
                if "key" in metadata.keys() :
                    metadata = {}
                    val.parameters['metadata'] = {}
                val.save()
                print(val.name)