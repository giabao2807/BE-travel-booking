from django.db.models import TextChoices


class BankCodes(TextChoices):
    NCB = "NCB"
    VISA = "VISA"
    MASTER_CARD = "MasterCard"
    JCB = "JCB"
