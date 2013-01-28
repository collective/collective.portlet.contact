# -*- coding: utf-8 -*-

import unittest2 as unittest

from pyquery import PyQuery

#from collective.portlet.contact import testing
from collective.portlet.contact.tests import base
from AccessControl.unauthorized import Unauthorized
PROJECTNAME = "collective.portlet.contact"


class IntegrationTestControlPanel(base.IntegrationTestCase):

    def setUp(self):
        super(IntegrationTestControlPanel, self).setUp()
        self.name = 'cpc-controlpanel'

    def test_view(self):
        traverse = self.portal.restrictedTraverse
        self.assertRaises(Unauthorized, traverse, (self.name,))
        self.setRoles(['Manager'])
        view = traverse(self.name)
        self.assertIsNotNone(view)
        html = view.render()
        pq = PyQuery(html)
        backend = pq('#form\\.backend')
        self.assertEqual(len(backend), 1)
        values = backend.children()
        self.assertEqual(len(values), 2)
        value1 = values[0]
        value2 = values[1]
        self.assertEqual(value1.attrib['value'], '')
        self.assertEqual(value2.attrib['value'], 'dummy')
        self.assertEqual(value2.attrib['selected'], 'selected')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
