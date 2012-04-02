from collective.portlet.contact.browser import jpegPhoto as base

from collective.portlet.contact.interfaces import IPortletContactUtility
from collective.portlet.contact.browser.ldap import utils
from collective.portlet.contact.i18n import MessageFactory as _
from collective.portlet.contact.utils import getPropertySheet

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from collective.portlet.contact.utils import getPropertySheet

from plone.app.z3cform import layout
from zope import interface
from zope import schema
from zope.component import getUtility
from z3c.form import button, field, form
from z3c.form.interfaces import HIDDEN_MODE
from OFS.Image import Image
from StringIO import StringIO

from collective.portlet.contact.browser.ldap.utils import LdapServer
import ldap
from ldap import modlist

class jpegPhoto(base.jpegPhoto):
    """return the jpeg photo get from uid
       or '' if an error occured (photo unavailable in LDAP and no default 
       photo provided)"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getFrom_ldap(self, uid):
        config = get_properties(self.context)
        utility = getUtility(IPortletContactUtility, name='ldap')

        entries = utility._search(self.context, search_on='uid',
                        attrs=['jpegPhoto'],
                        query=uid)

        has_ldap_photo = len(entries) > 0 \
                         and entries[0]['datas']['jpegPhoto'] is not None
        if not has_ldap_photo:
            return ''
        data = entries[0]['datas']['jpegPhoto']
        return data

class Form(base.Form):

    def setPhoto_ldap(self, data):
        photo = data['photo']
        #check the content type of the uploaded file
        content_type = self.widgets['photo'].value.headers['content-type']
        if content_type != 'image/jpeg':
            raise form.interfaces.WidgetActionExecutionError(
                   'photo', interface.Invalid(_(u'Is not a JPEG photo')))
        #try to set the photo to the contact
        try:
            _setPhoto_ldap(self.context, data['uid'], photo)
        except ldap.SERVER_DOWN:
            raise form.interfaces.ActionExecutionError(
                    interface.Invalid(
                    _("The LDAP server is unreacheable")))
        except ldap.INVALID_CREDENTIALS:
            raise form.interfaces.ActionExecutionError(
                    interface.Invalid(
                    _("The LDAP authentication credentials are invalid")))
        except ldap.NO_SUCH_OBJECT:
            raise form.interfaces.ActionExecutionError(
                    interface.Invalid(
                    _("The entry you have specified is not in the LDAP")))
        except ldap.INSUFFICIENT_ACCESS:
            raise form.interfaces.ActionExecutionError(
                    interface.Invalid(
                    _("The LDAP credentials provided has not the modify permission.")))

        IStatusMessage(self.request).addStatusMessage(
                                      _(u"The photo has been well uploaded"))
        self.request.response.redirect(self.context.absolute_url()+'/view')

    def getLDAPConfig(self):
        config = {}
        pp = getPropertySheet(self.context)
        config['host'] = pp.ldap_server_host
        config['port'] = pp.ldap_server_port
        config['user'] = pp.ldap_bind_dn
        config['password'] = pp.ldap_bind_password
        config['basedn'] = pp.ldap_search_base
        if pp.ldap_search_recursive:
            config['scope'] = ldap.SCOPE_SUBTREE
        else:
            config['scope'] = ldap.SCOPE_ONELEVEL
        return config


class Page(layout.FormWrapper):

    form = Form

def _setPhoto_ldap(context, uid , photo):
    props = getPropertySheet(context)

    if props.ldap_search_recursive:
        SCOPE = ldap.SCOPE_SUBTREE
    else:
        SCOPE = ldap.SCOPE_ONELEVEL
        
    server = LdapServer(props.ldap_server_host,
                        props.ldap_server_port,
                        props.ldap_bind_dn,
                        props.ldap_bind_password,
                        props.ldap_search_base,
                        SCOPE)
    server.connect()
    entries = server.search('uid', uid, attrs=['jpegPhoto'])

    contact = entries[0]['datas']
    old_photo = contact.get('jpegPhoto')
    if old_photo:
        old_photo = old_photo[0]
    else:
        old_photo = ''
    old = {'jpegPhoto':old_photo}
    new = {'jpegPhoto':photo}

    ldif = modlist.modifyModlist(old,new)
    server.l.modify_s(entries[0]['path'],ldif)
    server.close()
