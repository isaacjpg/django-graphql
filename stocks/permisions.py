

def is_authenticated(func):

  def wrapper(cls, info, **kwargs):
    if not info.context.user:
      raise Exception("You are not authorized to perform operations")

    return func(cls, info, **kwargs)

  return wrapper
  