from typing import List

from api_general.models import Image
from base.consts.cloudinary import CloudinaryFolder
from base.services import CloudinaryService


class ImageService:
    @classmethod
    def create_images(cls, list_image_link):
        rs = []
        for image in list_image_link:
            img = Image(link=image)
            img.save()
            img = Image.objects.filter(link=image).first()
            rs.append(img)
        return rs

    @classmethod
    def bulk_create_related_model_images(cls, image_files: list, related_image_model, related_model_field: str, related_model_value):
        if image_files:
            links = CloudinaryService.upload_list_image(image_files, CloudinaryFolder.HOTEL_IMAGES_PICTURE.value)
            images: List[Image] = [Image(link=link) for link in links]
            Image.objects.bulk_create(images)

            image_ids = Image.objects.filter(link__in=links).values_list("id", flat=True)
            related_model_images: List[related_image_model] = []
            for image_id in image_ids:
                related_model_images.append(
                    related_image_model(**{"image_id": image_id, related_model_field: related_model_value})
                )
            related_image_model.objects.bulk_create(related_model_images)
