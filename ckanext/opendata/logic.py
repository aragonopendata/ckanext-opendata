from __future__ import division
import math

from pylons import config
from dateutil.parser import parse as dateutil_parse

from ckan.plugins import toolkit


import logging


log = logging.getLogger(__name__)




@toolkit.auth_allow_anonymous_access
def opendata_auth(context, data_dict):
    '''
    All users can access DCAT endpoints by default
    '''
    return {'success': True}

       
