from tastypie.resources import ModelResource
from doppel2.core.models import ScalarData


class ScalarDataResource(ModelResource):
    class Meta:
        queryset = ScalarData.objects.all()
        resource_name = 'scalar_data'
