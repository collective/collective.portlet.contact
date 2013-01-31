# -*- coding: utf-8 -*-

from zope import component
from zope import schema
from zope.interface import implements
from zope.formlib import form
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

#from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider, IPortletRetriever
from plone.app.portlets.portlets import base

from collective.portlet.contact.i18n import MessageFactory as _

from zope.app.form.browser.textwidgets import TextWidget
from collective.portlet.contact.addressbook import IAddressBook
PORTLET_PATH = "%(context_path)s/++%(category)sportlets++%(manager)s/%(id)s"


class AutocompleteContactTextWidget(TextWidget):

    def __init__(self, *args):
        super(AutocompleteContactTextWidget, self).__init__(*args)

    autocomplete = ViewPageTemplateFile('autocomplete.pt')

    def __call__(self):
        html = super(AutocompleteContactTextWidget, self).__call__()
        return html + self.autocomplete()


class IContactPortlet(IPortletDataProvider):
    """A portlet which renders the results of a contact search.
    """

    header = schema.TextLine(title=_(u"Portlet header"),
                             description=_(u"Title of the rendered portlet"),
                             required=True)

    contact = schema.TextLine(title=_(u"Contact"),
                              description=_(u"The contact to display."),
                              required=True)

    contact_id = schema.TextLine(title=_(u"Contact uniq id"),
                                 description=_(u"The contact uniq id."),
                                 required=True)


class Assignment(base.Assignment):
    """
    Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IContactPortlet)

    header = u""
    contact = u""

    def __init__(self, header=u"", contact=u"", contact_id=""):
        self.header = header
        self.contact = contact
        self.contact_id = contact_id

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    index = ViewPageTemplateFile('contact.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.addressbook = None
        self.settings = None

    def update(self):
        if self.addressbook is None:
            self.addressbook = IAddressBook(self.context)
            self.addressbook.update()
        if self.settings is None:
            self.settings = self.addressbook.settings

    def render(self):
        self.update()
        return self.index()

    @memoize
    def getContactInfo(self):
        """ get the contact informations the portlet is pointing to"""
        if self.load_ajax():
            return "ajax"  # not None
        uniq_id = self.data.contact_id
        return self.addressbook.getContactInfos(uniq_id)

    def portlet_url(self):
        portlet_url = ""
        portal_state = component.getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        portal_url = portal_state.portal_url()
        portal = portal_state.portal()
        portal_path = '/'.join(portal.getPhysicalPath())

        retriever = component.getMultiAdapter(
            (self.context, self.manager), IPortletRetriever
        )
        category = None

        for info in retriever.getPortlets():
            if info['assignment'] is self.data.aq_base:
                category = info['category']
                key = info['key']
                break

        if category is not None:
            path = key[len(portal_path) + 1:]
            info = {'category': category,
                    'id': '%s' % self.data.id,
                    'manager': self.manager.__name__,
                    'context_path': path}
            portlet_url = '%s/%s' % (portal_url, PORTLET_PATH % info)
        return portlet_url

    def load_ajax(self):
        """return True if the portlet should be load in ajax"""
        if hasattr(self.settings, 'ajax'):
            return self.settings.ajax
        return False


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """

    form_fields = form.Fields(IContactPortlet)
    form_fields['contact'].custom_widget = AutocompleteContactTextWidget

    label = _(u"title_add_contact_portlet",
              default=u"Add contact portlet")
    description = _(u"description_contact_portlet",
                    default=u"A portlet which can display a contact.")

    def setUpWidgets(self, ignore_request=False):
        super(AddForm, self).setUpWidgets(ignore_request=ignore_request)
        self.widgets['contact'].displayWidth = 50
        self.widgets['contact_id'].type = 'hidden'

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """

    form_fields = form.Fields(IContactPortlet)
    form_fields['contact'].custom_widget = AutocompleteContactTextWidget

    label = _(u"title_edit_contact_portlet",
              default=u"Edit contact text portlet")
    description = _(u"description_contact_portlet",
                    default=u"A portlet which can display a contact.")

    def setUpWidgets(self, ignore_request=False):
        super(EditForm, self).setUpWidgets(ignore_request=ignore_request)
        self.widgets['contact'].displayWidth = 50
        self.widgets['contact_id'].type = 'hidden'
