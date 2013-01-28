# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface, implements
from zope.component import adapts
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from plone.app.controlpanel.form import ControlPanelForm
try:
    from plone.app.controlpanel.form import _template
except ImportError:
    _template = ControlPanelForm.template

from collective.portlet.contact.i18n import MessageFactory as _


class IPortletContactDummyControlPanel(Interface):

    dummy_fullname = schema.ASCIILine(
        title=_(u'Full name'),
        description=_(u''),
        required=False,
    )

    dummy_phone = schema.ASCIILine(
        title=_(u'Phone'),
        description=_(u''),
        required=False,
    )

    dummy_mail = schema.ASCIILine(
        title=_(u'Mail'),
        description=_(u''),
        required=False,
    )

    dummy_employee_type = schema.ASCIILine(
        title=_(u'Employee Type'),
        description=_(u''),
        required=False,
    )

    dummy_photo_url = schema.ASCIILine(
        title=_(u'Photo URL'),
        description=_(u''),
        required=False,
    )


class PortletContactDummyControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IPortletContactDummyControlPanel)

    def __init__(self, context):
        super(PortletContactDummyControlPanelAdapter, self).__init__(context)
        portal_properties = getToolByName(self.context, 'portal_properties')
        self.props = getattr(portal_properties, 'portlet_contact_properties')

    def setFullName(self, value):
        self.props.manage_changeProperties(dummy_fullname=value)

    def getFullName(self):
        return self.props.dummy_fullname
    dummy_fullname = property(getFullName, setFullName)

    def setPhone(self, value):
        self.props.manage_changeProperties(dummy_phone=value)

    def getPhone(self):
        return self.props.dummy_phone
    dummy_phone = property(getPhone, setPhone)

    def setMail(self, value):
        self.props.manage_changeProperties(dummy_mail=value)

    def getMail(self):
        return self.props.dummy_mail
    dummy_mail = property(getMail, setMail)

    def setEmployeeType(self, value):
        self.props.manage_changeProperties(dummy_employee_type=value)

    def getEmployeeType(self):
        return self.props.dummy_employee_type
    dummy_employee_type = property(getEmployeeType, setEmployeeType)

    def setPhotoURL(self, value):
        self.props.manage_changeProperties(dummy_photo_url=value)

    def getPhotoURL(self):
        return self.props.dummy_photo_url
    dummy_photo_url = property(getPhotoURL, setPhotoURL)


class PortletContactDummyControlPanel(ControlPanelForm):
    """ collective.portlet.contact DUMMY Control Panel Form """

    implements(IPortletContactDummyControlPanel)

    base_template = _template
    template = ZopeTwoPageTemplateFile('controlpanel.pt')

    form_fields = form.FormFields(IPortletContactDummyControlPanel)

    label = _(u'Portlet Contact: configure DUMMY settings')
    description = ''
    form_name = _(u'Configure DUMMY settings')
