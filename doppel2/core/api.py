from doppel2.core.models import Site, Device, Person, Sensor
from rest_framework import views, viewsets, serializers, permissions
from rest_framework.response import Response
from django.conf.urls import patterns, url, include
from rest_framework import routers
from rest_framework.reverse import reverse


class Doppel2Serializer(serializers.HyperlinkedModelSerializer):
    @property
    def data(self):
        '''If a collection was requested (self.many is True), then we want to
        return the full collection resource, including its own URL'''
        data = super(Doppel2Serializer, self).data
        view_name = self.opts.model._meta.object_name.lower() + '-list'
        if self.many:
            data = {
                '_href': reverse(view_name, request=self.context['request']),
                '_type': 'resource-list',
                'data': data,
            }
        return data


class SensorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sensor
        exclude = ('url',)

    def _get_type(self, obj):
        return 'sensor'

    _href = serializers.HyperlinkedIdentityField(view_name='sensor-detail')
    _type = serializers.SerializerMethodField('_get_type')
    metric = serializers.SlugRelatedField(slug_field='name')
    unit = serializers.SlugRelatedField(slug_field='name')


class PersonSerializer(Doppel2Serializer):
    class Meta:
        model = Person
        exclude = ('url',)

    def _get_type(self, obj):
        return 'person'

    _href = serializers.HyperlinkedIdentityField(view_name='person-detail')
    _type = serializers.SerializerMethodField('_get_type')


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device
        exclude = ('url',)

    def _get_type(self, obj):
        return 'device'

    # the ModelViewSet calls the detail view device-detail by default
    _href = serializers.HyperlinkedIdentityField(view_name='device-detail')
    _type = serializers.SerializerMethodField('_get_type')
    sensors = SensorSerializer(many=True)
    # TODO: we need to figure out how to include this relationship. Right now
    # there's a circular dependency issue
    #site = SiteSerializer()


class SiteSerializer(Doppel2Serializer):
    class Meta:
        model = Site
        exclude = ('url',)

    def _get_type(self, obj):
        return 'site'

    # TODO: if the url model field is non-empty the _href field should point to
    # it instead of the URL on the local server
    _href = serializers.HyperlinkedIdentityField(view_name='site-detail')
    _type = serializers.SerializerMethodField('_get_type')
    people = PersonSerializer(many=True)
    devices = DeviceSerializer(many=True)


# This was the first attempt to get the right collection behavior, but
# it was abandoned because it didn't work well with nested collections
#class Doppel2ViewSet(viewsets.ModelViewSet):
#    '''This ViewSet superclass handles the custom format for list views
#    (collections) that we want for doppel2, namely that collections are
#    themselves actual resources and have their own _href and _type fields.'''
#
#    def list(self, request):
#        '''This implementation was mostly lifted from the one from the
#        ListModelMixin'''
#        self.object_list = self.filter_queryset(self.get_queryset())
#        list_data = self.get_serializer(self.object_list, many=True).data
#        view_name = resource_router.get_default_base_name(self) + '-list'
#        response = {
#            '_href': reverse(view_name, request=request),
#            'data': list_data,
#            '_type': 'list',
#        }
#        return Response(response)


class SiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    """
    represents a device, yo.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class PersonViewSet(viewsets.ModelViewSet):
    """
    represents a person, yo.
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class SensorViewSet(viewsets.ModelViewSet):
    """
    represents a sensor, yo.
    """
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class ApiRootView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        # note that we're passing in the request in the serializer context so
        # it knows how to render a full URL
        site_serializer = SiteSerializer(Site.objects.all(),
                                         many=True,
                                         context={'request': request})
        person_serializer = PersonSerializer(Person.objects.all(),
                                             many=True,
                                             context={'request': request})
        response = {
            '_href': reverse('api-root', request=request),
            '_type': 'api-root',
            'sites': site_serializer.data,
            'person': person_serializer.data
        }
        return Response(response)


resource_router = routers.SimpleRouter()
resource_router.register('sites', SiteViewSet)
resource_router.register('people', PersonViewSet)
resource_router.register('devices', DeviceViewSet)
resource_router.register('sensors', SensorViewSet)

urls = patterns(
    '',
    url(r'^$', ApiRootView.as_view(), name='api-root'),
    url(r'^', include(resource_router.urls)),
)
