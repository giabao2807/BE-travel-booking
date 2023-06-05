from api_general.services import ImageService
from api_tour.models import TourImage


class TourImageService:
    @classmethod
    def create_tour_image(cls, tour, tour_images_link):
        images = ImageService.create_images(tour_images_link)
        tour_images = [TourImage(tour=tour, image=image) for image in images]
        TourImage.objects.bulk_create(tour_images)
