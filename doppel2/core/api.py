from tastypie.resources import ModelResource, Resource
from tastypie import fields
from tastypie.constants import ALL
from doppel2.core.models import ScalarData


class ScalarDataResource(ModelResource):
    class Meta:
        queryset = ScalarData.objects.all()
        resource_name = 'scalar_data'
        excludes = ['id']
        filtering = {
            'timestamp': ALL,
        }

    # add some additional fields from related models
    unit = fields.CharField()
    metric = fields.CharField()

    def dehydrate_unit(self, bundle):
        return bundle.obj.sensor.unit.name

    def dehydrate_metric(self, bundle):
        return bundle.obj.sensor.metric.name


class AggregateScalarDataResource(Resource):
    pass
