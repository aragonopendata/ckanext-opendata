import json
import logging
from pylons import config

from ckan.plugins import toolkit
import ckan.logic as logic

if toolkit.check_ckan_version(min_version='2.1'):
    BaseController = toolkit.BaseController
else:
    from ckan.lib.base import BaseController

import ckan.lib.base as base

import re

from time import time
from urllib import urlretrieve
from os import remove
import xlrd
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from json import JSONEncoder
import csv
import urllib
import htmllib
from StringIO import StringIO

from ckan.common import OrderedDict, request, response

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key

render = base.render
abort = base.abort


DEFAULT_GA_AOD_CORE_URL = "http://opendata.aragon.es/GA_OD_Core/download?view_id="
DEFAULT_GA_AOD_CORE_PATH='/var/www/wolfcms/GA_OD_Core'
DEFAULT_DOWNLOAD_TEMPORAL='/tmp'

GA_AOD_CORE_URL='ckanext.opendata.aodcore.url'
GA_AOD_CORE_PATH='ckanext.opendata.aodcore.path'
DOWNLOAD_TEMPORAL_PROP='ckanext.opendata.tempdir'

DOWNLOAD_TEMPORAL = config.get(DOWNLOAD_TEMPORAL_PROP,DEFAULT_DOWNLOAD_TEMPORAL)


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

        sys.path.insert(0, ga_aod_core_path_prop)
        import ga_od_core 
        import cx_Oracle
       
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
		log.error('#ShowVista: VistaId:' + str(vista_id))
   
		import urllib2
		showVistaURL = ga_aod_core_url_prop+str(vista_id)+"&select_sql=*&filter_sql=&formato="+str(vistaFormato)+"&name="+str(vistaNombre)
		log.error('ShowVistaURL: ' + showVistaURL)
		data = urllib2.urlopen(showVistaURL).read()
		if (vistaFormato == 'JSON'):
		    #response.headers['Content-Type'] = 'application/json;charset=utf-8'
		    response.headers = [('Content-Disposition', 'attachment; filename=\"' + str(vistaNombre) +"__ad" +  ".json" + '\"'),('Content-Type', 'application/json;charset=utf-8')]
		if (vistaFormato == 'CSV'):
		    #response.headers['Content-Type'] = 'text/csv;charset=utf-8'
		    response.headers = [('Content-Disposition', 'attachment; filename=\"' + str(vistaNombre)+ "__ad"+ ".csv" + '\"'),('Content-Type', 'text/csv;charset=utf-8')]
		if (vistaFormato == 'XML'):
		    response.headers['Content-Type'] = 'application/xml;charset=utf-8';
		    response.headers['Content-Disposition'] = 'attachment; filename=' + str(vistaNombre) + '.xml';
		if data is None:
		    return None
		else
		    return [data.encode('UTF-8')]
	except Exception,e:
		return e


    def data_resource(self, dataset, formato, version=None):
        """ Filter to resource rendering or download
                If resource doesn't exist, but a file with same name
                in XLS format does, it should be transformed to
                the required format (XML, JSON or CSV).
                Idem for Aragopedia resources
            """
        context = {'model': model, 'session': model.Session}

        fq = ' +dataset_type:dataset'
        q = 'name:' + dataset

        data_dict = {
                'q': q,
                'fq': fq.strip()
        }

        try:
            dataset_rsc = get_action('package_search')(context, data_dict)
            xlsAuto = {'csv', 'xml', 'json'}
            urlAuto = {'csv', 'xml', 'json', 'ttl'}
            for res in dataset_rsc['results']:
              for resource in res['resources']:
                if resource.get('format').lower() == formato.lower():
                  if version is None:
                    return redirect(resource.get('url'))
                  else:
                    if resource.get(formato.upper() + '_position') ==  version:
                      return redirect(resource.get('url'))

                if resource.get('format').lower() == 'xls' and formato.lower() in xlsAuto:
                  if version is None:
#                    return redirect(c.urlenco(unicode('http://opendata.aragon.es/catalogo/render/resource/' + resource.get('name') + '.' + formato).encode('utf8'), ':?=/&amp;%'))
                    return redirect(unicode('http://opendata.aragon.es/catalogo/render/resource/' + resource.get('name') + '.' + formato).encode('utf8'))
                  else:
                    if resource.get(formato.upper() + '_position') ==  version:
#                      return redirect(c.urlenco(unicode('http://opendata.aragon.es/catalogo/render/resource/' + resource.get('name') + '.' + formato).encode('utf8'), ':?=/&amp;%'))
                      return redirect(unicode('http://opendata.aragon.es/catalogo/render/resource/' + resource.get('name') + '.' + formato).encode('utf8'))

                if resource.get('format').lower() == 'url' and formato.lower() in urlAuto:
                  if version is None:
#                    return redirect(c.urlenco(unicode((rsc_dict['url'].split("?"))[0]+  '.ttl?api_key=e103dc13eb276ad734e680f5855f20c6&amp;_view=completa').encode('utf8'), ':?=/&amp;%'))
                    return redirect(unicode((resource['url'].split("?"))[0]+  '.ttl?api_key=e103dc13eb276ad734e680f5855f20c6&_view=completa').encode('utf8'))
                  else:
                    if resource.get(formato.upper() + '_position') ==  version:
#                     return redirect(c.urlenco(unicode((rsc_dict['url'].split("?"))[0]+  '.ttl?api_key=e103dc13eb276ad734e680f5855f20c6&amp;_view=completa').encode('utf8'), ':?=/&amp;%'))
                      return redirect(unicode((resource['url'].split("?"))[0]+  '.ttl?api_key=e103dc13eb276ad734e680f5855f20c6&_view=completa').encode('utf8'))

        except NotFound:
            abort(404, _('Resource not found'))

        
    def render_resource(self, resource_id):
        """ Filter to resource rendering or download
                If resource doesn't exist, but a file with same name
                in XLS format does, it should be transformed to
                the required format (XML, JSON or CSV)
            """
        
        
        log.debug('#RenderResource: Entrando en render resource')
        log.debug('#RenderResource: ResourceId: %s' % resource_id)
        
        context = {}
        log.debug('#RenderResource: Contexto creado')
        try:
            # Resource exists, redirect to the download URL
            rsc = get_action('resource_show')(context, {'id': resource_id})
            log.debug('#RenderResource: Devolviendo resource_show')
            return redirect(rsc['url'])
        except NotFound:
            # Resource doesn't exist, we search for a XLS file with same name
            log.debug('#RenderResource: entrando en NotFound')
            xls_resource_id = re.sub("\.\w{3,4}$", ".xls", resource_id)
            log.debug('#RenderResource: xls_resource_id %s' % xls_resource_id)
            try:
                rsc = get_action('resource_show')(context,
                                                  {'id': xls_resource_id})
                log.debug('#RenderResource: rsc %s' % rsc)
            except NotFound:
                # Some resources has no extension...
                try:
                    xls_resource_id = re.sub("\.\w{3,4}$", "", resource_id)
                    log.debug('#RenderResource:Step 2 xls_resource_id %s' % xls_resource_id)
                    results = get_action('resource_search')(context,
                                                      {'query': 'name:' + xls_resource_id})

                    rsc = results['results'][0]

                    log.debug('#RenderResource: rsc %s' % rsc)
                    log.debug('#RenderResource: url %s' % rsc['url'])
                except:
                    #print xls_resource_id + " not_found"
                    log.debug('#RenderResource: Resource not found')
                    abort(404, 'Resource not found')

        if rsc['url'] is None:
            abort(404, 'Resource not found')

        log.debug('#RenderResource: Downloading XLS: %s' % rsc['url'])
        xls_file = self._download_xls_file(rsc['url'])
        format = re.search("\.(\w{3,4})$", resource_id).group(1).lower()
        log.debug('#RenderResource: Formato a generar: %s' % format)
        if format == 'xml':
            content_to_render = self._xls_to_xml(xls_file)
        elif format == 'json':
            content_to_render = self._xls_to_json(xls_file)
        elif format == 'csv':
            content_to_render = self._xls_to_csv(xls_file)
        else:
            remove(xls_file)
            abort(404, _('Resource not found'))

        remove(xls_file)
        log.debug('#RenderResource: Devolviendo valor')
        #return render('package/resource_render.html', loader_class=NewTextTemplate)
        return content_to_render

    def _create_json_index(self, data):
        data_wo_ids = self._remove_fields(data['results'])
        return JSONEncoder(ensure_ascii=False, indent=4).encode(data_wo_ids)

    def _create_xml_index(self, data):
        xml = self._serialize_xml(data['results'], 'datasets')
        return self._indent_xml(xml)


    def _serialize_xml(self, root, name):
        xml = ET.Element(name)
        if isinstance(root, dict):
            for key in root.keys():
                if key not in BLACKLIST:
                    xml.append(self._serialize_xml(root[key], key))
        elif isinstance(root, list):
            for item in root:
                xml.append(self._serialize_xml(item, 'item'))
        elif isinstance(root, bool) or isinstance(root, int):
            xml.text = str(root)
        else:
            xml.text = root
        return xml

    def _remove_fields(self, root):
        data = root
        if isinstance(data, dict):
            for key in data.keys():
                if key not in BLACKLIST:
                    data[key] = self._remove_fields(data[key])
                else:
                    del data[key]
        elif isinstance(data, list):
            for item in data:
                item = self._remove_fields(item)
        return data



    def _download_xls_file(self, url):
        """ Download a xls with random name to hard disk"""
        dest = DOWNLOAD_TEMPORAL + "/" + str(int(time()*100)) + ".xls"
        urlretrieve(url, dest)
        return dest

    def _indent_xml(self, xml):
        raw_xml = ET.tostring(xml, 'utf-8')
        reparsed = minidom.parseString(raw_xml)
        return reparsed.toprettyxml()


    def _xls_to_xml(self, xls_file):
        """ Prepare a xml string based on a xls file """
        xml_filename = re.sub("\.xls", ".xml", xls_file)
        root = ET.Element("root")
        xls = xlrd.open_workbook(xls_file)
        for sheet_xls in xls.sheets():
            sheet_xml = ET.Element("sheet")
            sheet_xml.attrib["name"] = sheet_xls.name
            for row in range(sheet_xls.nrows):
                row_xml = ET.Element("row")
                row_xml.attrib["name"] = str(row)
                for value in sheet_xls.row_values(row):
                    value_xml = ET.Element("value")
                    if isinstance(value, unicode):
                        value_xml.text = value
                    else:
                        value_xml.text = str(value)
                    row_xml.append(value_xml)
                sheet_xml.append(row_xml)
            root.append(sheet_xml)
        return self._indent_xml(root)

    def _xls_to_json(self, xls_file):
        """ Prepare a json string based on a xls file """
        xls = xlrd.open_workbook(xls_file)
        sheets = []
        for sheet_xls in xls.sheets():
            sheet_json = {'name': sheet_xls.name}
            rows = []
            for row in range(sheet_xls.nrows):
                row_json = {'name': str(row)}
                values = []
                for value in sheet_xls.row_values(row):
                    if isinstance(value, unicode):
                        values.append(value)
                    else:
                        values.append(value)
                row_json['values'] = values
                rows.append(row_json)
            sheet_json['rows'] = rows
            sheets.append(sheet_json)
        text = JSONEncoder(ensure_ascii=False, indent=4).encode(sheets)
        return text

    def _xls_to_csv(self, xls_file):
        xls = xlrd.open_workbook(xls_file)
        sheet = xls.sheet_by_index(0)
        csv_rows = []
        for sheet in xls.sheets():
            for row in range(sheet.nrows):
                csv_row = []
                for value in sheet.row_values(row):
                    if isinstance(value, float):
                        value_to_print = str(value)
                    else:
                        value_to_print = value
                    csv_row.append(value_to_print)
                csv_rows.append(', '.join(csv_row))
        text = '\n'.join(csv_rows)
        return text
