import graphene


from user_controller.schema import schema as user_schema
from products_controller.schema   import schema as product_schema


class Query(user_schema.Query, product_schema.Query,graphene.ObjectType):
  pass

class Mutation(user_schema.Mutation,graphene.ObjectType):
  pass

schema = graphene.Schema(query=Query, mutation=Mutation)