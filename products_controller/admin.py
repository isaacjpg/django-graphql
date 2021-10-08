from django.contrib import admin
from .models import Category, Product, ProductImage,Business

admin.site.register((Product,ProductImage,Category,Business))