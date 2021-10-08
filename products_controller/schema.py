import graphene
from graphene_django import DjangoObjectType
from stocks.permisions import paginate, is_authenticated, get_query
from django.db.models import Q

from .models import Category, Business, Product, ProductImage

class CategoryType(DjangoObjectType):
  class Meta:
    model=Category

class BusinessType(DjangoObjectType):
  class Meta:
    model=Business

class ProductType(DjangoObjectType):
  class Meta:
    model=Product

class ProductImageType(DjangoObjectType):
  class Meta:
    model=ProductImage

class Query(graphene.ObjectType):
  categories = graphene.List(CategoryType, name=graphene.String())
  business=graphene.List(BusinessType,name=graphene.String())
  
  products=graphene.Field(paginate(ProductType),
  search=graphene.String(),
  min_price=graphene.Float(), 
  max_price=graphene.Float(),
  category=graphene.String(),
  business=graphene.String(), sort_by=graphene.String(),is_asc=graphene.Boolean(),page=graphene.Int())

  product=graphene.Field(ProductType,id=graphene.ID(required=True))

  def resolve_categories(self,info,name):
    query=Category.objects.prefetch_related("category_products").all()

    if name:
      query=query.filter(Q(name__icontains=name)|Q(name__iexact=name)).distinct()
    return query
  
  def resolve_businesss(self,info,name):
    query=Business.objects.prefetch_related("business_products")

    if name:
      query=query.filter(Q(name__icontains=name)|Q(name__iexact=name)).distinct()
    return query

  def resolve_products(self,info,**kwargs):
    query=Product.objects.select_related("category","business").prefetch_related("product_images")

    #Primero busco si tengo search, lo tomo de los kwargs
    if kwargs.get("search",None):
      qs=kwargs["search"]
      search_fields = (
        "sku","name","description","category__name","business__name"
      )

      search_data=get_query(qs,search_fields)
      query=query.filter(search_data)

    #Precio Mínimo
    if kwargs.get("min_price", None):
      qs=kwargs["min_price"]
      query=query.filter(Q(price__gt=qs)|Q(price=qs)).distinct()

     #Precio Máximo
    if kwargs.get("max_price", None):
      qs=kwargs["max_price"]
      print(qs)
      query=query.filter(Q(price__lt=qs)|Q(price=qs)).distinct()
    
    #Nombre de la categoría
    if kwargs.get("category", None):
      qs=kwargs["category"]
      query=query.filter(Q(category__name__icontains=qs)|Q(category__name__iexact=qs)).distinct()

    #Nombre del Business
    if kwargs.get("business", None):
      qs=kwargs["business"]
      query=query.filter(Q(business__name__icontains=qs)|Q(business__name__iexact=qs)).distinct()

    #Sorting
    if kwargs.get("sort_by", None):
      qs=kwargs["sort_by"]
      is_asc=kwargs.get("is_asc",False)

      if not is_asc:
        qs=f"-{qs}"
      
      query=query.order_by(qs)
    
    return query
  
  #Para un solo producto
  def resolve_product(self,info,id):
    query=Product.objects.select_related("category","business").prefetch_related("product_images").get(id=id)
    return query
  

schema=graphene.Schema(query=Query)

