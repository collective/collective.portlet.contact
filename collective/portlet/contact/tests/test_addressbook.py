# -*- coding: utf-8 -*-

import unittest2 as unittest

#from collective.portlet.contact import testing
from collective.portlet.contact.tests import base, utils
PROJECTNAME = "collective.portlet.contact"


class UnitTestAddressBook(base.UnitTestCase):

    def setUp(self):
        super(UnitTestAddressBook, self).setUp()
        from collective.portlet.contact.addressbook import AddressBook
        self.book = AddressBook(self.context)
        self.book.settings = utils.FakeSettings()
        self.book.backend = utils.FakeBackend()

    def test_search(self):
        self.book.backend.contacts['UUID'] = {'name': 'Test'}
        res = self.book.search(q="test")
        self.assertEqual(len(res), 1)
        self.assertIn('name', res[0])
        self.assertEqual('Test', res[0]['name'])

    def test_getContactInfos(self):
        self.book.backend.contacts['UUID'] = {'name': 'Test'}
        info = self.book.getContactInfos('UUID')
        self.assertIn('name', info)
        self.assertEqual('Test', info['name'])


class IntegrationAddressBookTestCase(base.IntegrationTestCase):

    def setUp(self):
        super(IntegrationAddressBookTestCase, self).setUp()
        from collective.portlet.contact.addressbook import AddressBook
        self.book = AddressBook(self.folder)

    def test_update(self):
        self.book.update()
        self.assertIsNotNone(self.book.backend)
        self.assertIsNotNone(self.book.settings)
        from collective.portlet.contact.dummy import addressbook
        self.assertIsInstance(self.book.backend, addressbook.DummyAddressBook)
        self.assertEqual(self.book.settings.ajax, False)
        self.assertEqual(self.book.settings.backend, 'dummy')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
