from django.contrib import admin
from .models import Unit, CostCategory, ProcessCategory, Cost, Process

admin.site.register((Unit,CostCategory,ProcessCategory,Cost,Process))


