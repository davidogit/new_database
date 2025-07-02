from django.contrib import admin
from .models import Tenant, InvestmentScheme, StaffAPI, Contribution, Membership
# Register your models here.
admin.site.register(Tenant)
admin.site.register(InvestmentScheme)
admin.site.register(StaffAPI)
admin.site.register(Contribution)
admin.site.register(Membership)

