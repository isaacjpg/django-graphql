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
  business=graphene.String(), 
  sort_by=graphene.String(),
  is_asc=graphene.Boolean(),page=graphene.Int())

  product=graphene.Field(ProductType,id=graphene.ID(required=True))

  def resolve_categories(self,info,name):
    query=Category.objects.prefetch_related("category_products").all()

    if name:
      query=query.filter(Q(name__icontains=name)|Q(name__iexact=name)).distinct()
    return query
  
  def resolve_business(self,info,name):
    query=Business.objects.prefetch_related("business_products").all()

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
  

class CreateBusiness(graphene.Mutation):
  business=graphene.Field(BusinessType)

  class Arguments:
    name=graphene.String(required=True)
  
  def mutate(self,info,name):
    instance = Business.objects.create(name=name)

    return CreateBusiness(
      business=instance 
    )

class UpdateBusiness(graphene.Mutation):
  business=graphene.Field(BusinessType)

  class Arguments:
    id=graphene.ID(required=True)
    name=graphene.String(required=True)

  def mutate(self,info,name,id):
    instance = Business.objects.get(id=id)
    instance.name=name
    instance.save()

    return UpdateBusiness(
      business=instance
    )

class CreateCategory(graphene.Mutation):
  Category=graphene.Field(CategoryType)

  class Arguments:
    name=graphene.String(required=True)
  
  def mutate(self,info,name):
    instance = Category.objects.create(name=name)

    return CreateCategory(
      Category=instance 
    )

class UpdateCategory(graphene.Mutation):
  Category=graphene.Field(CategoryType)

  class Arguments:
    id=graphene.ID(required=True)
    name=graphene.String(required=True)

  def mutate(self,info,name,id):
    instance = Category.objects.get(id=id)
    instance.name=name
    instance.save()

    return UpdateCategory(
      Category=instance
    )

#Se define como InputType los campos como una especie de Form
class ProductInput(graphene.InputObjectType):
  sku=graphene.String()
  name=graphene.String()
  price=graphene.Float()
  description=graphene.String()
  category_id=graphene.ID()
  business_id=graphene.ID()

#Definimos un InputType para los ProductImages
class ProductImageInput(graphene.InputObjectType):
  image_id=graphene.ID(required=True)
  is_cover=graphene.Boolean()

class CreateProduct(graphene.Mutation):
  product = graphene.Field(ProductType)

  class Arguments:
    product_data=ProductInput(required=True)
    #Se define como graphene List porque podemos ingresar varias imágenes
    images=graphene.List(ProductImageInput)
    
  def mutate(self,info,product_data,images):
    #Chequeamos si el nombre o el sky ya existen
    try:
      have_sku=Product.objects.filter(sku=product_data["sku"])
    except Exception:
      pass
    
    if have_sku:
      raise Exception("This sku already exist")

    try:
      have_name=Product.objects.filter(name=product_data["name"])
    except Exception:
      pass

    if have_name:
      raise Exception("This name already exist")

    #Creamos el producto
    product = Product.objects.create(**product_data)

    #Creamos la tabla de ProductImages
    ProductImage.objects.bulk_create([
      ProductImage(product_id=product.id,**image_data) for image_data in images
    ])

    return CreateProduct(
      product=product
    )

class UpdateProduct(graphene.Mutation):
  product = graphene.Field(ProductType)

  class Arguments:
    product_data=ProductInput()  
    product_id=graphene.ID(required=True)

  def mutate(self,info, product_data,product_id):
    #Chequeo si estoy tratando de actualizar el nombre a revisar si estoy incluyendo el nombre en el query
    #Pero esto me puede obligar a tener Querys condicionales en el Frontend
    #Lo otro es dejar que la BD envíe el error
    if product_data.get("name",None):
      try:
        have_name=Product.objects.filter(name=product_data["name"])
      except Exception:
        pass

      if have_name:
        raise Exception("This name already exist")
    
    if product_data.get("sku",None):
      try:
        have_sku=Product.objects.filter(sku=product_data["sku"])
      except Exception:
        pass

      if have_sku:
        raise Exception("This sku already exist")

    Product.objects.filter(id=product_id).update(**product_data)

    return UpdateProduct(
      product=Product.objects.get(id=product_id)
    )


class Mutation(graphene.ObjectType):
  create_businness=CreateBusiness.Field()
  update_business=UpdateBusiness.Field()
  create_category=CreateCategory.Field()
  update_category=UpdateCategory.Field()
  create_product=CreateProduct.Field()
  update_product=UpdateProduct.Field()


schema=graphene.Schema(query=Query, mutation=Mutation)

