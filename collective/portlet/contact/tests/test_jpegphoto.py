# -*- coding: utf-8 -*-

import unittest2 as unittest

#from collective.portlet.contact import testing
from collective.portlet.contact.tests import base, utils


class UnitTestJPEGPhoto(base.UnitTestCase):

    def setUp(self):
        super(UnitTestJPEGPhoto, self).setUp()
        from collective.portlet.contact.browser.jpegPhoto import jpegPhoto
        self.photo_view = jpegPhoto(self.context, self.request)
        self.photo_view.settings = utils.FakeSettings()
        self.photo_view.portal = utils.FakePortal()

    def test_call(self):
        res = self.photo_view()
        self.assertEqual(res, '')
        self.request.form['uid'] = 'uniq_id'
        self.photo_view()
        self.assertEqual(self.request.response.content, 'photo')


class IntegrationTestJPEGPhoto(base.IntegrationTestCase):

    def setUp(self):
        super(IntegrationTestJPEGPhoto, self).setUp()
        from collective.portlet.contact.browser.jpegPhoto import jpegPhoto
        self.photo_view = jpegPhoto(self.folder, self.request)
        self.photo_view.update()

    def test_call(self):
        res = self.photo_view()
        self.assertEqual(res, '')
        self.request.form['uid'] = 'uniq_id'
        self.photo_view()
        #TODO: test

    def test_getFrom_ofs(self):
        data = self.photo_view.getFrom_ofs('notexisting')
        self.assertEqual(data, '')

    def test_getFrom_default(self):
        data = self.photo_view.getFrom_default('notexisting')
        self.assertEqual(data, '')

    def test_getFrom_archetypes(self):
        method = self.photo_view.getFrom_archetypes
        self.assertRaises(NotImplementedError, method, ('unid_id',))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
