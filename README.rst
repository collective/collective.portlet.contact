Introduction
============

Display a contact in a Plone portlet.

Contacts are provided throw backends. When installed this addon is configured
to use the 'dummy' backend.

You can configure this addon to use an other backend:

* Dummy backend, used for tests
* LDAP backend (add python-ldap in your setup)
* SugarCRM backend (add the addon collective.sugarcrm)

Installation
============

.. image:: https://secure.travis-ci.org/collective/collective.js.galleria.png
    :target: http://travis-ci.org/collective/collective.js.galleria

This addon can be installed as installed as any other Plone addon, please
follow the official documentation_.

.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to


Possible problems
-----------------

* I have the following error: "We already have: zope.schema 3.5.4 but z3c.form 2.4.1 requires 'zope.schema>=3.6.0'."
    => You should add this extra version restriction to your buildout: http://good-py.appspot.com/release/plone.app.z3cform/0.5.0

Credits
=======

Companies
---------

|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact Makina Corpus <mailto:python@makina-corpus.org>`_


Authors
-------

- Sylvain BOURELIOU <sylvain.boureliou@gmail.com>

Contributors
------------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
