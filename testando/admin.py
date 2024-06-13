from django.contrib import admin
from django.contrib import admin
from .models import Images

# Register your models here.

class ImagesAdmin(admin.ModelAdmin):
    pass

admin.site.register(Images, ImagesAdmin)
