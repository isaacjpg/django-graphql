from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('first_name', "admin")
        extra_fields.setdefault('last_name', "admin")

        if not extra_fields.get("is_staff", False):
            raise ValueError('Superuser must have is_staff=True.')

        if not extra_fields.get("is_superuser", False):
            raise ValueError('Superuser must have is_staff=True.')

        return self.create_user(email, password)

class User(AbstractBaseUser, PermissionsMixin):
  email=models.EmailField(unique=True)
  first_name=models.CharField(max_length=100)
  last_name=models.CharField(max_length=100)
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)

  is_staff = models.BooleanField(default=False)
  is_active=models.BooleanField(default=True)

  USERNAME_FIELD="email"
  objects = UserManager()

  def __str__(self):
      return self.email

  def save(self,*args,**kwargs):
    super().full_clean()
    super().save(*args,**kwargs)  
      
class ImageUpload(models.Model):
    image=models.ImageField(upload_to="images")

    def __str__(self):
        return "{}{}{}".format(settings.S3_BUCKET_URL,settings.MEDIA_URL , self.image)

class UserProfile(models.Model):
    user=models.OneToOneField(User,related_name="user_profile",on_delete=models.CASCADE)
    profile_picture=models.ForeignKey(ImageUpload, related_name="user_images",on_delete=models.SET_NULL, null=True)
    phone=models.CharField(max_length=100,blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

