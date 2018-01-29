# -*- coding: utf-8 -*-
import os

import boto3
import reverse_geocoder as rg
from motionless import DecoratedMap, LatLonMarker
GMAPS_API_KEY_PARAM = os.getenv("GMAPS_API_KEY_PARAM", "/google/mapsapi")

ssm = boto3.client('ssm')
GMAPS_API_KEY = ssm.get_parameter(Name=GMAPS_API_KEY_PARAM)['Parameter']['Value']


def unicode_flag(code):
    OFFSET = 127397
    points = map(lambda x: ord(x) + OFFSET, code.upper())
    return ('\\U%08x\\U%08x' % tuple(points)).decode('unicode-escape')


def build_tweet(results):
    status = []
    dmap = DecoratedMap(size_x=640, size_y=320, key=GMAPS_API_KEY)
    for result in rg.search([tuple(res[0]) for res in results]):
        status.append(", ".join([result['name'], result['admin1'], unicode_flag(result['cc'])]))
    for index, result in enumerate(results):
        dmap.add_marker(LatLonMarker(result[0][0], result[0][1], label=str(index+1)))
    img_url = dmap.generate_url()
    return '\n'.join(status), img_url
