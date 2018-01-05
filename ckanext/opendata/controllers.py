import json
import logging
from pylons import config

from ckan.plugins import toolkit

if toolkit.check_ckan_version(min_version='2.1'):
    BaseController = toolkit.BaseController
else:
    from ckan.lib.base import BaseController



DEFAULT_GA_AOD_CORE_URL = "http://opendata.aragon.es/GA_OD_Core/download?view_id="
DEFAULT_GA_AOD_CORE_PATH='/var/www/wolfcms/GA_OD_Core'

GA_AOD_CORE_URL='ckanext.opendata.aodcore.url'
GA_AOD_CORE_PATH='ckanext.opendata.aodcore.path'


log = logging.getLogger(__name__)

def check_access_header():
    _format = None

    # Check Accept headers
    accept_header = toolkit.request.headers.get('Accept', '')
    if accept_header:
        _format = parse_accept_header(accept_header)
    return _format


class OpendataController(BaseController):

    def opendata_showVista(self):
        log.error('#ShowVista: Entrando en showVista ....')
        
        import os
        import sys
        ga_aod_core_url_prop = config.get(GA_AOD_CORE_URL,DEFAULT_GA_AOD_CORE_URL)
        ga_aod_core_path_prop = config.get(GA_AOD_CORE_PATH,DEFAULT_GA_AOD_CORE_PATH)

        log.error('#ShowVista: Param  ga_aod_core_url_prop: ' + ga_aod_core_url_prop)
        log.error('#ShowVista: Param  ga_aod_core_path_prop: ' + ga_aod_core_path_prop)

        '''import urllib2
        data = urllib2.urlopen('http://samplecsvs.s3.amazonaws.com/Sacramentorealestatetransactions.csv')

        log.debug('#ShowVista: Returning ...')
        return data'''

        sys.path.insert(0, ga_aod_core_path_prop)
        import ga_od_core 
        params = dict(request.params.items())
	try:        
	    if params:
                vistaResourceId = params.get('id')
                vistaNombre = params.get('name').encode('utf8')
                vistaFormato = params.get('formato')
                log.error('#ShowVista: vistaResourceId:' + vistaResourceId)
                log.error('#ShowVista: vistaNombre:' + vistaNombre)
                log.error('#ShowVista: vistaFormato: ' + vistaFormato)
	except Exception,e:      
        log.error('#ShowVista: Parametros incorrectos') 
	    return 'You missed some param'
	try:        
	    vista_id = ga_od_core.get_view_id(vistaResourceId)
        log.error('#ShowVista: VistaId:' + vista_id) 
   
        import urllib2
        data = urllib2.urlopen(ga_aod_core_url_prop+str(vista_id)+"&select_sql=*&filter_sql=&formato="+str(vistaFormato)).read()

        if (vistaFormato == 'JSON'):
            #response.headers['Content-Type'] = 'application/json;charset=utf-8'
            response.headers = [('Content-Disposition', 'attachment; filename=\"' + str(vistaNombre) +"__ad" +  ".json" + '\"'),('Content-Type', 'application/json;charset=utf-8')]
        if (vistaFormato == 'CSV'):
            #response.headers['Content-Type'] = 'text/csv;charset=utf-8'

            response.headers = [('Content-Disposition', 'attachment; filename=\"' + str(vistaNombre)+ "__ad"+ ".csv" + '\"'),('Content-Type', 'text/csv;charset=utf-8')]
        if (vistaFormato == 'XML'):
            response.headers['Content-Type'] = 'application/xml;charset=utf-8';
            response.headers['Content-Disposition'] = 'attachment; filename=' + str(vistaNombre) + '.xml';     
        return data
    except Exception,e:        
	    return 'Something went wrong. please try again or contact your administrator'       
        #data = ga_od_core.download(vista_id,None,None,vistaFormato,None,None)

    


