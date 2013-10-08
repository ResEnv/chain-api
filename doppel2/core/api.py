from doppel2.core.models import Site, Device, Person, Sensor
from rest_framework import viewsets, serializers


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


class SiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Site
        exclude = ('url',)

    def _get_type(self, obj):
        return 'site'

    # TODO: if the url model field is non-empty the _href field should point to
    # it instead of the URL on the local server
    _href = serializers.HyperlinkedIdentityField(view_name='site-detail')
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
    site = SiteSerializer()


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        exclude = ('url',)

    def _get_type(self, obj):
        return 'person'

    _href = serializers.HyperlinkedIdentityField(view_name='person-detail')
    _type = serializers.SerializerMethodField('_get_type')


#class RootSerializer(serializers.Serializer):
#    '''The root resource that will serve as the main entry point into
#    the API. Currently it only includes a list of sites'''
#    sites = SiteSerializer(many=True)


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
