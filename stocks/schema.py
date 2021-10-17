import graphene


from user_controller.schema import schema as user_schema
from products_controller.schema   import schema as product_schema
from costs_controller import schema as costs_schema

class Query(user_schema.Query, costs_schema.Query, product_schema.Query,graphene.ObjectType):
  pass

class Mutation(user_schema.Mutation, costs_schema.Mutation, product_schema.Mutation, graphene.ObjectType):
  pass

schema = graphene.Schema(query=Query, mutation=Mutation)