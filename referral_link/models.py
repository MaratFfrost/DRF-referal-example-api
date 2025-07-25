from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import random
import string


def generate_referral_code() -> str:
    characters = string.digits + string.ascii_letters
    code = ''.join(random.choice(characters) for _ in range(6))
    if not code.isalpha() and code.upper() != code:
        return code
    else:
        return generate_referral_code()


class ReferralLinkUser(AbstractUser):
    phone_number = models.CharField(
        max_length=15,
        unique=True,
    )

    referral_code = models.CharField(
        max_length=6,
        unique=True,
        default=generate_referral_code,
    )

    invited_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.phone_number} (код: {self.referral_code})"

    def clean(self):
        if self.invited_by and self.pk and self.invited_by_id == self.pk:
            raise ValidationError("Нельзя указать себя как пригласившего.")

    def save(self, *args, **kwargs):
        self.clean()

        if not self.referral_code:
            self.referral_code = generate_referral_code()

        if self.pk:
            original = ReferralLinkUser.objects.get(pk=self.pk)
            if (self.referral_code == original.referral_code) and (self.invited_by == original.invited_by):
                super().save(*args, **kwargs)
                return

        while ReferralLinkUser.objects.filter(referral_code=self.referral_code).exclude(pk=self.pk).exists():
            self.referral_code = generate_referral_code()

        super().save(*args, **kwargs)
