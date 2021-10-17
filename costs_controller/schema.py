import graphene
from graphene_django  import DjangoObjectType
from stocks.permisions import is_authenticated, paginate, is_authenticated, get_query
from django.db.models import Q

from .models import Unit, CostCategory, ProcessCategory, Cost, Process

class UnitType(DjangoObjectType):
  class Meta:
    model=Unit

class CostCategoryType(DjangoObjectType):
  class Meta:
    model=CostCategory

class ProcessCategoryType(DjangoObjectType):
  class Meta:
      model=ProcessCategory

class Query(graphene.ObjectType):
  units=graphene.List(UnitType)
  costCategories=graphene.List(CostCategoryType)
  processCategories=graphene.List(ProcessCategoryType)
  
  def resolve_units(self,info):
    return Unit.objects.all()
  
  def resolve_costCategories(self,info):
    return CostCategory.objects.all()
  
  def resolve_processCategories(self,info):
    return ProcessCategory.objects.all()

class CreateCostCategory(graphene.Mutation):
  cost_category=graphene.Field(CostCategoryType)

  class Arguments:
    name=graphene.String(required=True)

  def mutate(self,info,name):
    instance=CostCategory.objects.create(name=name)

    return CreateCostCategory(
      cost_category=instance
    )

class UpdateCostCategory(graphene.Mutation):
  cost_category=graphene.Field(CostCategoryType)

  class Arguments:
    cost_category_id=graphene.ID(required=True)
    name=graphene.String(required=True)
  
  def mutate(self,info,cost_category_id,name):
    CostCategory.objects.filter(id=cost_category_id).update(name=name)
    
    return UpdateCostCategory(
      cost_category=CostCategory.objects.get(id=cost_category_id)
    )

class DeleteCostCategory(graphene.Mutation):
  success=graphene.Boolean()

  class Arguments:
    cost_category_id=graphene.ID(required=True)
  
  def mutate(self,info,cost_category_id):
    instance=CostCategory.objects.get(id=cost_category_id)

    try:
      count=instance.costs.count()
    except Exception:
      pass
    if count>0:
      raise Exception("Category has associated costs")

    instance.delete()
    return DeleteCostCategory(
      success=True
    )

class CreateProcessCategory(graphene.Mutation):
  process_category=graphene.Field(ProcessCategoryType)

  class Arguments:
    name=graphene.String(required=True)

  def mutate(self,info,name):
    instance=ProcessCategory.objects.create(name=name)

    return CreateProcessCategory(
      process_category=instance
    )

class UpdateProcessCategory(graphene.Mutation):
  process_category=graphene.Field(ProcessCategoryType)

  class Arguments:
    process_category_id=graphene.ID(required=True)
    name=graphene.String(required=True)
  
  def mutate(self,info,process_category_id,name):
    ProcessCategory.objects.filter(id=process_category_id).update(name=name)
    
    return UpdateProcessCategory(
      process_category=ProcessCategory.objects.get(id=process_category_id)
    )

class DeleteProcessCategory(graphene.Mutation):
  success=graphene.Boolean()

  class Arguments:
    process_category_id=graphene.ID(required=True)
  
  def mutate(self,info,process_category_id):
    instance=ProcessCategory.objects.get(id=process_category_id)

    try:
      count=instance.processes.count()
    except Exception:
      pass
    if count>0:
      raise Exception("Category has associated Processes")

    instance.delete()
    return DeleteProcessCategory(
      success=True
    )


class Mutation(graphene.ObjectType):
  create_cost_category=CreateCostCategory.Field()
  update_cost_category=UpdateCostCategory.Field()
  delete_cost_category=DeleteCostCategory.Field()
  create_process_category=CreateProcessCategory.Field()
  update_process_category=UpdateProcessCategory.Field()
  delete_process_category=DeleteProcessCategory.Field()

schema=graphene.Schema(query=Query, mutation=Mutation)