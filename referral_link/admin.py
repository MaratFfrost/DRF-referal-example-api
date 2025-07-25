from django.contrib import admin
from .models import ReferralLinkUser

# Register your models here.


@admin.register(ReferralLinkUser)
class ReferralLinkUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'referral_code', 'invited_by',)
    search_fields = ('phone_number', 'referral_code')
    list_filter = ('invited_by',)
