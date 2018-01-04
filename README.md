## Installation


1. . /<CKAN_HOME>/bin/activate

2. cd <CKAN_HOME>/src

3.  Install the extension on your virtualenv:

        (pyenv) $ pip install -e git+https://github.com/aragonopendata/ckanext-opendata.git#egg=ckanext-opendata

4.  Install the extension requirements:

        (pyenv) $ pip install -r ckanext-opendata/requirements.txt


5. Set properties in production.ini

add custom_opendata to plugin
set
ckanext.opendata.aodcore.url=AOD_CORE url
ckanext.opendata.aodcore.path=path to aod_core


