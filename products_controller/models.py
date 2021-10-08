from django.db import models

from user_controller.models import ImageUpload

class Category(models.Model):
  name = models.CharField(max_length=100, unique=True)
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.name

class Business(models.Model):
  name = models.CharField(max_length=100, unique=True)
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.name

class Product(models.Model):
  category=models.ForeignKey(Category, related_name="category_products",on_delete=models.CASCADE)
  business=models.ForeignKey(Business, related_name="business_products",on_delete=models.CASCADE)
  sku = models.CharField(max_length=100, unique=True)
  name = models.CharField(max_length=100, unique=True)
  price=models.FloatField()
  description=models.TextField()
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.name
  
  class Meta:
    ordering=("sku",)

class ProductImage(models.Model):
  product=models.ForeignKey(Product, related_name="product_images", on_delete=models.CASCADE)
  image=models.ForeignKey(ImageUpload,related_name="images_product",on_delete=models.CASCADE)
  is_cover=models.BooleanField(default=False)
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.image
  

