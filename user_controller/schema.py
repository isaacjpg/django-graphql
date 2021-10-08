import graphene
from graphene.types import schema
from .models import User,ImageUpload, UserProfile 
from graphene_django import DjangoObjectType
from django.contrib.auth import authenticate
from datetime import datetime
from stocks.authentication import TokenManager
from stocks.permisions import is_authenticated, paginate
from graphene_file_upload.scalars import Upload
from django.conf import settings

class UserType(DjangoObjectType):
  
  class Meta:
    model=User

class UserProfileType(DjangoObjectType):
  class Meta:
    model = UserProfile

class ImageUploadType(DjangoObjectType):
  image = graphene.String()
  
  class Meta:
    model=ImageUpload
  
  def resolve_image(self,info):
    if(self.image):
      return "{}{}{}".format(settings.S3_BUCKET_URL,settings.MEDIA_URL , self.image)
    return None
  

class RegisterUser(graphene.Mutation):
  status = graphene.Boolean()
  message= graphene.String()

  class Arguments:
    email = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    password= graphene.String(required=True)

  def mutate(self,info,email,password,first_name, last_name):
    User.objects.create_user(email,password,first_name,last_name)

    return RegisterUser(
      status=True,
      message="User created successfulyy"
    )

class LoginUser(graphene.Mutation):
  access = graphene.String()
  refresh = graphene.String()
  user = graphene.Field(UserType)

  class Arguments:
    email = graphene.String(required=True)
    password= graphene.String(required=True)

  def mutate(self,info,email,password):
    user = authenticate(username=email, password=password)

    if not user:
      raise Exception("invalid credentials")

    user.last_login=datetime.now()
    user.save()

    access = TokenManager.get_access({"user_id":user.id})
    refresh = TokenManager.get_refresh({"user_id":user.id})

    return LoginUser(
      access=access,
      refresh=refresh,
      user=user
    )

class GetAccess(graphene.Mutation):
  access = graphene.String()

  class Arguments:
    refresh = graphene.String(required=True)

  def mutate(self,info,refresh):
    token = TokenManager.decode_token(refresh)

    if not token or token["type"] != "refresh":
      raise Exception("Invalid token or has expired")
    
    access = TokenManager.get_access({"user_id":token["user_id"]})

    return GetAccess(
      access=access
    )

class ImageUploadMain(graphene.Mutation):
  image=graphene.Field(ImageUploadType)

  class Arguments:
    image=Upload(required=True)

  def mutate(self,info,image):
    image=ImageUpload.objects.create(image=image)

    return ImageUploadMain(image=image)

class UserProfileInput(graphene.InputObjectType):
  #profile_picture_id=graphene.Int()
  phone=graphene.String()


class CreateUserProfile(graphene.Mutation):
  phone=graphene.String()
  profile_picture=graphene.String()

  class Arguments:
    phone=graphene.String()
    profile_picture_id=graphene.Int()

  @is_authenticated
  def mutate(self,info, **kwargs):
    user_profile=UserProfile.objects.create(
      user_id=info.context.user.id,
       **kwargs
    )

    return CreateUserProfile(
      phone=user_profile.phone,
      profile_picture=user_profile.profile_picture
    )

class UpdateUserProfile(graphene.Mutation):
  phone=graphene.String()
  profile_picture=graphene.String()

  class Arguments:
    phone=graphene.String()
    profile_picture_id=graphene.Int()

  @is_authenticated
  def mutate(self,info, **kwargs):
    try:
      info.context.user.user_profile
    except Exception:
      raise Exception("You dont have a profile to update")
    #Hago el Update
    user_profile=UserProfile.objects.filter(user__id=info.context.user.id).update(**kwargs)

    #Busco el Objecto para retornarlo en la Mutación
    user_profile=UserProfile.objects.get(user__id=info.context.user.id)

    #Retorno la mutación
    return UpdateUserProfile(
      phone=user_profile.phone,
      profile_picture=user_profile.profile_picture
    )

class Query(graphene.ObjectType):
  users=graphene.Field(paginate(UserType), page=graphene.Int())
  image_uploads=graphene.Field(paginate(ImageUploadType),page=graphene.Int())
  me = graphene.Field(UserType)

  @is_authenticated 
  def resolve_users(self,info,**kwargs):
    return User.objects.filter(**kwargs)
  
  def resolve_images(self,info,**kwargs):
    return ImageUpload.objects.filter(**kwargs)
  
  @is_authenticated
  def resolve_me(self,info):
    return info.context.user 

class Mutation(graphene.ObjectType):
  register_user=RegisterUser.Field()
  login_user=LoginUser.Field()
  get_access=GetAccess.Field()
  image_uploads=ImageUploadMain.Field()
  create_user_profile=CreateUserProfile.Field()
  update_user_profile=UpdateUserProfile.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)