from django.contrib import admin
from .models import User, ImageUpload,UserProfile

admin.site.register((User,ImageUpload,UserProfile,))

# Register your models here.
