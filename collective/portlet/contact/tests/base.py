# -*- coding: utf-8 -*-

import unittest2 as unittest

from collective.portlet.contact import testing
from collective.portlet.contact.tests import utils


class UnitTestCase(unittest.TestCase):

    def setUp(self):
        from ZPublisher.tests.testPublish import Request
        super(UnitTestCase, self).setUp()
        self.context = utils.FakeContext()
        self.request = Request()


class IntegrationTestCase(unittest.TestCase):

    layer = testing.INTEGRATION_TESTING

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']


class FunctionalTestCase(unittest.TestCase):

    layer = testing.FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']


def build_test_suite(test_classes):
    suite = unittest.TestSuite()
    for klass in test_classes:
        suite.addTest(unittest.makeSuite(klass))
    return suite
