import os, sys

from setuptools import setup, find_packages

version = '0.1'

def read(*rnames):
    return open(
        os.path.join('.', *rnames)
    ).read()

long_description = ('\n'.join((
    read('collective', 'portlet', 'contact', 'README.txt'), ''
    'Detailed Documentation',
    '**********************', '',
    read('docs', 'HISTORY.txt'), '',
    'Download',
    '********', ''
)))

open('doc.txt', 'w').write(long_description)

classifiers = [
    "Framework :: Plone",
    "Framework :: Zope2",
    "Programming Language :: Python",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Software Development :: Libraries :: Python Modules",]

setup(
    name='collective.portlet.contact',
    namespace_packages=['collective', 'collective.portlet',],
    version=version,
    description='Display LDAP contacts in Plone portlets.',
    long_description=long_description,
    classifiers=classifiers,
    keywords='plone portlet ldap contact',
    author='Sylvain Boureliou',
    author_email='sylvain.boureliou@makina-corpus.com',
    url='http://www.makina-corpus.com',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
    ],
    # define there your console scripts
    entry_points="""
    # -*- Entry points: -*-
    """,

)