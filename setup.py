import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-tenant-users',
    version='0.3.5',
    packages=[
        'tenant_users',
        'tenant_users.tenants',
        'tenant_users.tenants.migrations',
        'tenant_users.permissions',
        'tenant_users.permissions.migrations',
    ],
    include_package_data=True,
    license='MIT License', 
    description='A Django app to extend django-tenant-schemas to incorporate global multi-tenant users',
    long_description=README,
    url='https://www.github.com/Corvia/django-tenant-users',
    author='Corvia Technologies, LLC',
    author_email='support@corvia.tech',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8', 
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
