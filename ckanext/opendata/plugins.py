from pylons import config

from ckan import plugins as p
try:
    from ckan.lib.plugins import DefaultTranslation
except ImportError:
    class DefaultTranslation():
        pass


from ckanext.opendata.logic import (opendata_auth,)



DEFAULT_URL_ENDPOINT = '/catalogo/dataset'
CUSTOM_ENDPOINT_CONFIG = 'ckanext.opendata.catalog_endpoint'
ENABLE_CONTENT_NEGOTIATION_CONFIG = 'ckanext.opendata.enable_content_negotiation'

class OpendataPlugin(p.SingletonPlugin, DefaultTranslation):

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions, inherit=True)
    p.implements(p.IAuthFunctions, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    if p.toolkit.check_ckan_version(min_version='2.5.0'):
        p.implements(p.ITranslation, inherit=True)

    # IConfigurer
    def update_config(self, config):
       
        # Check custom catalog endpoint
        custom_endpoint = config.get(CUSTOM_ENDPOINT_CONFIG)
        if custom_endpoint:
            if not custom_endpoint[:1] == '/':
                raise Exception(
                    '"{0}" should start with a backslash (/)'.format(
                        DEFAULT_URL_ENDPOINT))
            if '{_format}' not in custom_endpoint:
                raise Exception(
                    '"{0}" should contain {{_format}}'.format(
                        DEFAULT_URL_ENDPOINT))

    # IRoutes
    def before_map(self, _map):

        controller = 'ckanext.opendata.controllers:OpendataController'

        _map.connect('showIndex',DEFAULT_URL_ENDPOINT + '/index/catalogo_opendata.{formato}',
                     controller=controller, action='opendata_showIndex',
                     requirements={})

        
        _map.connect('showVista',DEFAULT_URL_ENDPOINT + '/showVista',
                     controller=controller, action='opendata_showVista',
                     requirements={})

        #URLS mapeadas para compatibilidad con la anterior version

               
        _map.connect('renderView','/catalogo/render/resource/{resource_id}',
                     controller=controller, action='render_resource',
                     requirements={})
        _map.connect('renderData','/catalogo/data/{dataset}/{formato}',
                     controller=controller, action='data_resource',
                     requirements={})
        _map.connect('renderDataVersion','/catalogo/data/{dataset}/{formato}/{version}',
                     controller=controller, action='data_resource',
                     requirements={})     

        
        return _map

    # IActions
    def get_actions(self):
        return {
            
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'opendata_showVista': opendata_auth,
            'render_resource':opendata_auth,
            'data_resource':opendata_auth,
            'opendata_showIndex': opendata_auth,
        }

