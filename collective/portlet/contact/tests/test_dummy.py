# -*- coding: utf-8 -*-

import unittest2 as unittest

#from collective.portlet.contact import testing
from collective.portlet.contact.tests import base, utils
PROJECTNAME = "collective.portlet.contact"
KEYS = ('fullname', 'phonenumber', 'mail', 'employeetype', 'photourl')


class UnitTestDummy(base.UnitTestCase):

    def setUp(self):
        super(UnitTestDummy, self).setUp()
        from collective.portlet.contact.dummy.addressbook import DummyAddressBook
        self.book = DummyAddressBook(self.context)
        self.book.properties = utils.FakeSettings()

    def test_search(self):
        res = self.book.search(q="foo")
        self.assertEqual(len(res), 1)
        contact = res[0]
        self.assertEqual(contact, 'Foo Bar - foo@bar.co|uniq_id')

        res = self.book.search(q="test")
        self.assertEqual(len(res), 0)

    def test_getContactInfos(self):
        info = self.book.getContactInfos('notexisting')
        self.assertIsNone(info)
        info = self.book.getContactInfos('uniq_id')
        self.assertIsNotNone(info)
        for k in KEYS:
            self.assertIn(k, info)
        sheet = self.book.properties
        self.assertEqual(info['fullname'], sheet.dummy_fullname)
        self.assertEqual(info['phonenumber'], sheet.dummy_phone)
        self.assertEqual(info['employeetype'], sheet.dummy_employee_type)
        self.assertEqual(info['photourl'], sheet.dummy_photo_url)


class IntegrationTestDummy(base.IntegrationTestCase):

    def setUp(self):
        super(IntegrationTestDummy, self).setUp()
        from collective.portlet.contact.dummy.addressbook import \
            DummyAddressBook
        self.book = DummyAddressBook(self.folder)

    def test_update(self):
        self.assertIsNone(self.book.properties)
        self.book.update()
        self.assertIsNotNone(self.book.properties)
        self.assertEqual(self.book.properties.ajax, False)
        self.assertEqual(self.book.properties.backend, 'dummy')

    def test_getContactInfos(self):
        info = self.book.getContactInfos('notexisting')
        self.assertIsNone(info)
        info = self.book.getContactInfos('uniq_id')
        self.assertIsNotNone(info)
        for k in KEYS:
            self.assertIn(k, info)
        sheet = self.book.properties
        self.assertEqual(info['fullname'], sheet.dummy_fullname)
        self.assertEqual(info['phonenumber'], sheet.dummy_phone)
        self.assertEqual(info['employeetype'], sheet.dummy_employee_type)
        self.assertEqual(info['photourl'], sheet.dummy_photo_url)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
