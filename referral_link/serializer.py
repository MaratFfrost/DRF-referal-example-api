from rest_framework import serializers

from .models import ReferralLinkUser as rlu


class ReferralLinkUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = rlu
        fields = ['phone_number', ]
