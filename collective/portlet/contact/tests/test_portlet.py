import unittest2 as unittest

from pyquery import PyQuery
from zope.component import getUtility, getMultiAdapter

from plone.portlets import interfaces
from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.contact.portlet import contact
from collective.portlet.contact.tests.base import IntegrationTestCase


class IntegrationTestPortlet(IntegrationTestCase):

    def setUp(self):
        super(IntegrationTestPortlet, self).setUp()
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            interfaces.IPortletType,
            name='collective.portlet.contact.Contact')
        self.assertEquals(portlet.addview,
                          'collective.portlet.contact.Contact')

    def test_interfaces(self):
        # TODO: Pass any keyword arguments to the Assignment constructor
        portlet = contact.Assignment()
        self.assertTrue(interfaces.IPortletAssignment.providedBy(portlet))
        data = portlet.data
        self.assertTrue(interfaces.IPortletDataProvider.providedBy(data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            interfaces.IPortletType,
            name='collective.portlet.contact.Contact')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        data = {'header': u'Dummy', 'contact_id': u'uniq_id'}
        addview.createAndAdd(data=data)

        self.assertEquals(len(mapping), 1)
        self.assertIsInstance(mapping.values()[0], contact.Assignment)

    def test_invoke_edit_view(self):
        # NOTE: This test can be removed if the portlet has no edit form
        mapping = PortletAssignmentMapping()
        request = self.request

        mapping['foo'] = contact.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertIsInstance(editview, contact.EditForm)

    def test_obtain_renderer(self):
        context = self.folder
        request = self.request
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(interfaces.IPortletManager,
                             name='plone.rightcolumn',
                             context=self.portal)

        data = {'header': u'Dummy', 'contact_id': u'uniq_id'}
        assignment = contact.Assignment(**data)

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment),
            interfaces.IPortletRenderer)
        self.assertIsInstance(renderer, contact.Renderer)


class IntegrationTestRenderer(IntegrationTestCase):

    def setUp(self):
        super(IntegrationTestRenderer, self).setUp()
        self.setRoles(('Manager', ))

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            interfaces.IPortletManager,
            name='plone.rightcolumn',
            context=self.portal)

        data = {'header': u'Dummy', 'contact_id': u'uniq_id'}
        assignment = assignment or \
            contact.Assignment(**data)
        return getMultiAdapter((context, request, view, manager, assignment),
                               interfaces.IPortletRenderer)

    def test_render(self):
        data = {'header': u'Dummy', 'contact_id': u'uniq_id'}
        r = self.renderer(context=self.portal,
                          assignment=contact.Assignment(**data))
        r = r.__of__(self.folder)
        r.update()
        pq = PyQuery(r.render())
        avatar = pq('img')
        self.assertEqual(len(avatar), 1)
        self.assertEqual(avatar.attr['itemprop'], 'image')
        src = '++resource++collective-portlet-contact/defaultUser.png'
        self.assertEqual(avatar.attr['src'], src)

        fullname = pq('#fullname')
        self.assertEqual(fullname.attr['itemprop'], 'name')
        self.assertEqual(fullname.text(), 'Foo Bar')
        employee_type = pq('#employeetype')
        self.assertEqual(employee_type.attr['itemprop'], 'jobTitle')
        self.assertEqual(employee_type.text(), 'Developer')
        mail = pq('#mail')
        self.assertEqual(mail.attr['itemprop'], 'email')
        script = mail.children()[0]
        self.assertEqual(script.tag, 'script')
        encoded = "eval(unescape('%64%6F%63%75%6D%65%6E%74%2E%77%72%69%74%65%"\
            "28%27%3C%61%20%68%72%65%66%3D%22%6D%61%69%6C%74%6F%3A%66%6F%6F%4"\
            "0%62%61%72%2E%63%6F%6D%22%3E%66%6F%6F%40%62%61%72%2E%63%6F%6D%3C"\
            "%2F%61%3E%27%29'))"
        self.assertEqual(script.text, encoded)
        phone = pq('#phonenumber')
        self.assertEqual(phone.attr['itemprop'], 'telephone')
        self.assertEqual(phone.text(), '+33 (0) 111 222 333')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
