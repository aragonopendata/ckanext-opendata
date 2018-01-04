from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name='ckanext-opendata',
    version=version,
    description="Plugin para la implementación de funcionalidades personalizadas de DGA - Openadta",
    long_description='''\
    ''',
    classifiers=[],
    keywords='',
    author='David Figueroa Alejandro',
    author_email='david.figueroa.alejandro@gmail.com',
    url='https://github.com/opendata/ckanext-opendata',
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.opendata'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''

    [ckan.plugins]
      
    opendata_custom=ckanext.opendata.plugins:OpendataPlugin

    },
)
