import random
from random import randint

import string
from datetime import date


def rand_string_gen(size=6, chars=string.ascii_uppercase + string.digits):
  """Returns a randomly generated string of length size consisting of the
  character set chars
  """
  return ''.join(random.choice(chars) for _ in range(size))

def rand_date(start, end):
  """Returns a tuple of two randomly generated datetime objects between the
  start and end seed dates
  """
  # convert dates to epoch representation
  start_ordinal = start.toordinal()
  end_ordinal = end.toordinal()
  # generate a random date between start and end
  rand_start_day = randint(start_ordinal, end_ordinal)
  rand_end_day = randint(start_ordinal, end_ordinal)
  # make sure end is after start
  while rand_end_day < rand_start_day:
    rand_end_day = randint(start_ordinal, end_ordinal)

  return (date.fromordinal(rand_start_day), date.fromordinal(rand_end_day))
