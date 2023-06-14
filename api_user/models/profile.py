from django.core.validators import RegexValidator, MinLengthValidator
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from api_user.managers import ProfileManager
from api_user.models import Role
from base.models import TimeStampedModel
from base.models.fields import TinyIntegerField


class Profile(AbstractBaseUser, TimeStampedModel):
    class GenderChoices(models.IntegerChoices):
        MALE = 1
        FEMALE = 2
        OTHER = 3
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    password = models.CharField(max_length=255)
    avatar = models.CharField(max_length=200, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    gender = TinyIntegerField(choices=GenderChoices.choices, default=GenderChoices.OTHER)
    birthday = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    phone = models.CharField(
        max_length=11,
        null=True,
        validators=[
            RegexValidator(regex=r"^\d+$", message="A valid integer is required."),
            MinLengthValidator(9),
        ],
    )

    USERNAME_FIELD = 'email'
    objects = ProfileManager()

    class Meta:
        db_table = 'profiles'
