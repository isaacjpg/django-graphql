from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL


class Unit(models.Model):
  name=models.CharField(max_length=100,unique=True)
  code=models.CharField(max_length=100,unique=True)

  def __str__(self):
    return self.name

class ProcessCategory(models.Model):
  name=models.CharField(max_length=100,unique=True)

  def __str__(self):
    return self.name

class CostCategory(models.Model):
  name=models.CharField(max_length=100, unique=True)

  def __str__(self):
    return self.name

class Cost(models.Model):
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)
  sku=models.CharField(max_length=100,unique=True)
  name=models.CharField(max_length=100)
  category=models.ForeignKey(CostCategory, on_delete=models.CASCADE, related_name='costs')
  unit=models.ForeignKey(Unit,on_delete=models.CASCADE)
  minPrice=models.FloatField(default=0)
  grams=models.FloatField(default=0)
  amorNew=models.FloatField(default=0)
  amorRep=models.FloatField(default=0)

  def __str__(self):
    return self.name

class Process(models.Model):
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)
  sku=models.CharField(max_length=100,unique=True)
  name=models.CharField(max_length=100)
  category=models.ForeignKey(ProcessCategory,on_delete=models.CASCADE, related_name='processes')
  unit=models.ForeignKey(Unit, on_delete=models.CASCADE)
  isPrinting=models.BooleanField(default=False)
  mermaFix=models.FloatField(default=0)
  mermaVar=models.FloatField(default=0)
  setupTime=models.FloatField(default=0)
  speed=models.FloatField(default=0)
  machine=models.IntegerField(null=True,blank=True)
  costs=models.ManyToManyField(Cost)

  def __str__(self):
    return self.name
