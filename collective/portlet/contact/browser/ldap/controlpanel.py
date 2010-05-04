# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface, implements
from zope.component import adapts
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from plone.app.controlpanel.form import ControlPanelForm, _template

from collective.portlet.contact.i18n import MessageFactory as _

class IPortletContactLdapControlPanel(Interface):

    ldap_server_host = schema.ASCIILine(title=_(u'label_ldap_server',
                                        default=u'LDAP server'),
                                description=_(u'help_ldap_server',
                                              default=u'The address or hostname of the LDAP server.'),
                                required=True)

    ldap_server_port = schema.Int(title=_(u'label_ldap_server_port',
                                        default=u'LDAP port'),
                                description=_(u'help_ldap_server_port',
                                              default=u'The system port of the LDAP server.'),
                                required=True)

    ldap_bind_dn = schema.ASCIILine(title=_(u'label_ldap_bind_dn',
                                        default=u'Bind DN'),
                                description=_(u'help_ldap_bind_dn',
                                              default=u'The DN of a manager account in the LDAP directory. '
                                              'This must be allowed to access all user informations.'),
                                required=True)

    ldap_bind_password = schema.ASCIILine(title=_(u'label_ldap_bind_password',
                                        default=u'Bind password'),
                                description=_(u'help_ldap_bind_password',
                                              default=u'Password to use when binding to the LDAP server.'),
                                required=True)

    ldap_search_base = schema.ASCIILine(title=_(u'label_ldap_search_base',
                                        default=u'Base DN for contacts'),
                                description=_(u'help_ldap_search_base',
                                              default=u'This is the location in your LDAP directory where '
                                              'all users are stored.'),
                                required=True)

    ldap_search_recursive = schema.Bool(title=_(u'label_search_recursive',
                                        default=u'Search recursively for contacts'),
                                description=_(u'help_search_recursive',
                                              default=u'If True the LDAP server will search for users0 '
                                              'directly in the user base location and will also look in '
                                              'subfolders of the user base location.'),
                                required=False)

    ldap_default_photo_path = schema.ASCIILine(title=_(u'label_ldap_default_photo_path',
                                        default=u'Path to a default photo (ATImage) in your Plone site (ex: images/contact-photo.jpg)'),
                                description=_(u'help_ldap_default_photo_path',
                                              default=u'This photo will be used if the LDAP contact has no associated photo.'),
                                required=True)

class PortletContactLdapControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IPortletContactLdapControlPanel)

    def __init__(self, context):
        super(PortletContactLdapControlPanelAdapter, self).__init__(context)
        portal_properties = getToolByName(self.context, 'portal_properties')
        self.props = getattr(portal_properties, 'portlet_contact_properties')
        
    def setServerHost(self, value):
        self.props.manage_changeProperties(ldap_server_host=value)
    def getServerHost(self):
        return self.props.ldap_server_host
    ldap_server_host = property(getServerHost, setServerHost)

    def setServerPort(self, value):
        self.props.manage_changeProperties(ldap_server_port=value)
    def getServerPort(self):
        return self.props.ldap_server_port
    ldap_server_port = property(getServerPort, setServerPort)

    def setBindDn(self, value):
        self.props.manage_changeProperties(ldap_bind_dn=value)
    def getBindDn(self):
        return self.props.ldap_bind_dn
    ldap_bind_dn = property(getBindDn, setBindDn)

    def setBindPassword(self, value):
        self.props.manage_changeProperties(ldap_bind_password=value)
    def getBindPassword(self):
        return self.props.ldap_bind_password
    ldap_bind_password = property(getBindPassword, setBindPassword)

    def setSearchBase(self, value):
        self.props.manage_changeProperties(ldap_search_base=value)
    def getSearchBase(self):
        return self.props.ldap_search_base
    ldap_search_base = property(getSearchBase, setSearchBase)

    def setSearchRecursive(self, value):
        self.props.manage_changeProperties(ldap_search_recursive=value)
    def getSearchRecursive(self):
        return self.props.ldap_search_recursive
    ldap_search_recursive = property(getSearchRecursive, setSearchRecursive)

    def setDefaultPhotoPath(self, value):
        self.props.manage_changeProperties(ldap_default_photo_path=value)
    def getDefaultPhotoPath(self):
        return self.props.ldap_default_photo_path
    ldap_default_photo_path = property(getDefaultPhotoPath, setDefaultPhotoPath)

class PortletContactLdapControlPanel(ControlPanelForm):
    """ collective.portlet.contact LDAP Control Panel Form """

    implements(IPortletContactLdapControlPanel)

    base_template = _template
    template = ZopeTwoPageTemplateFile('controlpanel.pt')

    form_fields = form.FormFields(IPortletContactLdapControlPanel)

    label = _(u'Portlet Contact: configure LDAP settings')
    description = ''
    form_name = _(u'Configure LDAP settings')

