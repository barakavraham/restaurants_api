from flask import Blueprint
from flask_restful import Api

api_blueprint = Blueprint('api', __name__)
base_api = Api(api_blueprint)


class SubpathApi:
    def __init__(self, api, subpath, subendpoint):
        self._api = api
        self._subpath = subpath
        self._subendpoint = subendpoint

    def add_resource(self, resource, *urls, **kwargs):
        urls = [f'{self._subpath}{url}' for url in urls]
        endpoint = kwargs.pop('endpoint', resource.__name__.lower())
        kwargs['endpoint'] = f'{self._subendpoint}_{endpoint}' if endpoint else self._subendpoint
        return self._api.add_resource(resource, *urls, **kwargs)


# import APIs
from app.api.restaurant import *
