from django.contrib import admin
from .models import ShopUser, ShopUserProfile
from basketapp.models import Basket

admin.site.register(ShopUser)
admin.site.register(Basket)
admin.site.register(ShopUserProfile)
