# -*- coding: utf-8 -*-
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

from settings import *

# flask core settings
TESTING = True

# flask wtf settings
CSRF_ENABLED = False

PRESERVE_CONTEXT_ON_EXCEPTION = False

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'testing.db')
