from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from houses.models import House, Country
from houses.serializers import HouseSerializer
from silk.profiling.profiler import silk_profile


class HousePlainSerializer(object):

    @staticmethod
    def serialize_data(queryset):
        # print (type(queryset[0]))
        # print (queryset[0].id)
        return [
            {
                'id': entry.id,
                'address': entry.address,
                'country': entry.country.name,
                'sq_meters': entry.sq_meters,
                'price': entry.price
            } for entry in queryset
        ]

class HouseListAPIView(ListAPIView):
    model = House
    serializer_class = HouseSerializer
    plain_serializer_class = HousePlainSerializer  # <-- added custom serializer

    country = None

    @silk_profile(name='View Blog Post')
    def get_queryset(self):
        country = get_object_or_404(Country, pk=self.country)
        queryset = self.model.objects.filter(country=country).select_related('country').only('id', 'address', 'country', 'sq_meters', 'price')
        return queryset

    def list(self, request, *args, **kwargs):
        # Validation code to check for `country` param should be here
        country = self.request.GET.get("country")

        # self.country = Hasher.to_object_pk(country)
        self.country = country
        queryset = self.get_queryset()

        # serializer = self.serializer_class(queryset, many=True)
        # data = self.plain_serializer_class.serialize_data(queryset)
        data = self.plain_serializer_class.serialize_data(queryset)  # <-- serialize


        # return Response(serializer.data)
        return Response(data)
