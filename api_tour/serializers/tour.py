from rest_framework.serializers import ModelSerializer

from api_tour.models import Tour, TourImage


class TourSerializer(ModelSerializer):

    class Meta:
        model = Tour
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['city'] = instance.city.name if instance.city else 'Việt Nam'
        ret['rate'] = 4.5
        tour_image = TourImage.objects.filter(tour=instance)
        ret['list_images'] = [image.image.link for image in tour_image]
        return ret


class SortTourSerializer(ModelSerializer):

    class Meta:
        model = Tour
        fields = ('id', 'descriptions', 'cover_picture',
                  'total_days', 'language_tour', 'price',
                  'rate', 'num_review', 'city')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['city'] = instance.city.name if instance.city else 'Việt Nam'
        ret['rate'] = 4.5
        return ret
