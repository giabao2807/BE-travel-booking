from api_general.models import Image


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
