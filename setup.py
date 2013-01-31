import os
from setuptools import setup, find_packages

version = '1.1'

setup(
    name='collective.portlet.contact',
    namespace_packages=['collective', 'collective.portlet', ],
    version=version,
    description='Display LDAP contacts in Plone portlets.',
    long_description=open("README.rst").read() + "\n" +
                     open(os.path.join("docs", "HISTORY.txt")).read(),
    classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Framework :: Zope2",
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
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
        'plone.app.z3cform'
    ],
    extras_require=dict(test=['plone.app.testing', 'pyquery', 'fakeldap']),
    # define there your console scripts
    entry_points="""
    # -*- Entry points: -*-
    """,

)
