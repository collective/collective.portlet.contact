Introduction
============

Display a contact in a Plone portlet.

Two backends are provided, thez are responsible to retrieve the contact's 
informations:

  * Dummy backend, used for tests
  * LDAP backend 

Installation
============

Requirements
------------

  * python-ldap if you want to use the LDAP backend
  * tested with Plone 3.3.5, Plone 4.0

See docs/INSTALL.txt for installation instructions.

Possible problems
------------

  * I have the following error: "We already have: zope.schema 3.5.4 but z3c.form 2.4.1 requires 'zope.schema>=3.6.0'."
    => You should add this extra version restriction to your buildout: http://good-py.appspot.com/release/plone.app.z3cform/0.5.0

Credits
=======

Companies
---------

|makinacom|_

  * `Planet Makina Corpus <http://www.makina-corpus.org>`_
  * `Contact us <mailto:python@makina-corpus.org>`_


Authors
-------

  - Sylvain BOURELIOU <sylvain.boureliou@gmail.com>

Contributors
------------

  - JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
  