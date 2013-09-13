from tastypie.resources import ModelResource
from doppel2.core.models import ScalarData


class ScalarDataResource(ModelResource):
    class Meta:
        queryset = ScalarData.objects.all()
        resource_name = 'scalar_data'
        excludes = ['id']

    def dehydrate(self, bundle):
        bundle.data['unit'] = bundle.obj.sensor.unit.name
        bundle.data['metric'] = bundle.obj.sensor.metric.name
        return bundle
