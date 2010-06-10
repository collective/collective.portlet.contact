# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface, implements
from zope.component import adapts, getMultiAdapter
from zope.formlib import form
from zope.event import notify
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from plone.app.controlpanel.form import ControlPanelForm
try:
    from plone.app.controlpanel.form import _template
except ImportError:
    _template = ControlPanelForm.template

from plone.app.controlpanel.events import ConfigurationChangedEvent
from plone.app.form.validators import null_validator
from plone.protect import CheckAuthenticator
from Products.statusmessages.interfaces import IStatusMessage

from collective.portlet.contact.i18n import MessageFactory as _

class IPortletContactControlPanel(Interface):

    backend = schema.Choice(title=_(u'Back-end'),
                            description=_(u'Select the back-end for the Contact portlets.'),
                            vocabulary='collective.portlet.contact.utilities',
                            required=True)

class PortletContactControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IPortletContactControlPanel)

    def __init__(self, context):
        super(PortletContactControlPanelAdapter, self).__init__(context)
        portal_properties = getToolByName(self.context, 'portal_properties')
        self.props = getattr(portal_properties, 'portlet_contact_properties')
        
    def setBackend(self, value):
        self.props.manage_changeProperties(backend=value)
    def getBackend(self):
        return self.props.backend
    backend = property(getBackend, setBackend)
        
class PortletContactControlPanel(ControlPanelForm):
    """ collective.portlet.contact Control Panel Form """

    implements(IPortletContactControlPanel)

    base_template = _template
    template = ZopeTwoPageTemplateFile('controlpanel.pt')

    form_fields = form.FormFields(IPortletContactControlPanel)

    label = _(u'Portlet Contact: Select Back-end')
    description = ''
    form_name = _(u'Select Back-end')

    def _redirectToBackend(self):
        portal_properties = getToolByName(self.context, 'portal_properties')
        props = getattr(portal_properties, 'portlet_contact_properties')
        self.request.RESPONSE.redirect('@@cpc-controlpanel-%s' % props.backend)

    @form.action(_(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _("Changes saved, you can now configure the back-end.")
            notify(ConfigurationChangedEvent(self, data))
            self._on_save(data)
        else:
            self.status = _("No changes made.")

    @form.action(_(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return 

    @form.action(_(u'Configure the back-end'), validator=null_validator)
    def handle_go_to_backend(self, action, data):
       self._redirectToBackend()
        