# -*- coding: utf-8 -*-

import unittest2 as unittest

#from collective.portlet.contact import testing
from collective.portlet.contact.tests import base
PROJECTNAME = "collective.portlet.contact"


class IntegrationSetupTestCase(base.IntegrationTestCase):

    def setUp(self):
        super(IntegrationSetupTestCase, self).setUp()

    def test_installed(self):
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled(PROJECTNAME),
                        'package not installed')


class UninstallTestCase(base.IntegrationTestCase):

    def setUp(self):
        super(UninstallTestCase, self).setUp()
        qi = self.portal.portal_quickinstaller
        qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        qi = self.portal.portal_quickinstaller
        self.assertFalse(qi.isProductInstalled(PROJECTNAME),
                         'package not uninstalled')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
