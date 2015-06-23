import string
import random

def rand_string_gen(size=6, chars=string.ascii_uppercase + string.digits):
  """Returns a randomly generated string of length size consisting of the
  character set chars
  """
  return ''.join(random.choice(chars) for _ in range(size))
