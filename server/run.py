#!/usr/bin/env python
# -*- coding: utf-8 -*-
from application import create_app

app = create_app('settings')
app.run(host='0.0.0.0', port=5000, debug=True)
