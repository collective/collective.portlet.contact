from collective.portlet.contact.interfaces import IPortletContactUtility
from collective.portlet.contact.browser.ldap import utils
from collective.portlet.contact.i18n import MessageFactory as _
from collective.portlet.contact.utils import getPropertySheet
from collective.portlet.contact.browser.ldap.utils import LdapServer
import ldap
from ldap import modlist

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

def get_properties(context):
    props = getPropertySheet(context)
    config = {}
    config['default_photo_path'] = getattr(props, 'ldap_default_photo_path','')
    config['photo_storage'] = getattr(props, 'ldap_photo_storage', 'ofs')
    return config


class jpegPhoto(BrowserView):
    """return the jpeg photo get from uid
       or '' if an error occured (photo unavailable in LDAP and no default 
       photo provided)"""
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        request = self.request
        uid = request.get('uid', None)
        if not uid:
            return ''
        config = get_properties(self.context)
        storage = config['photo_storage']
        accessor = getattr(self, 'getFrom_'+storage)
        data = accessor(uid)
        if not data:
            data = self.getFrom_default(uid)
        self.request.response.setHeader('Content-Type', 'image/jpeg')
        self.request.response.write(data)

    def getFrom_ofs(self, uid):
        data = ''
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        photo = getattr(portal.portlet_contact_photo, uid, '')
        if photo:
            data = str(photo.data)
        return data

    def getFrom_archetypes(self, uid):
        raise NotImplementedError

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

        self.request.response.setHeader('Content-Type', 'image/jpeg')
        self.request.response.write(data)

    def getFrom_default(self, uid):
        config = get_properties(self.context)
        default_path = config['default_photo_path']
        
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        try:
            image = portal.unrestrictedTraverse(default_path)
            data = image.data
        except KeyError, AttributeError:
            self.context.plone_log('No valid default photo provided for collective.portlet.contact > LDAP backend')
            data = ''
        return data

class Schema(interface.Interface):
    """Schema to upload a photo to contact inside LDAP"""
    
    photo = schema.Bytes(title=_(u'Photo'),
                         description=_(u'Upload a jpeg photo.'),
                         #max_length=800000
                         )

    uid = schema.TextLine(title=_(u'Unique ID'),
                         description=_(u'The unique ID of the ldap entry.'),
                         )

class Form(form.Form):

    fields = field.Fields(Schema)
#    fields['photo'].widgetFactory[form.interfaces.INPUT_MODE] = namedfile.NamedImageWidget
    ignoreContext = True

    @property
    def label(self):
        return _(u"Contact\'s photo form ${cn}", mapping={'cn':self.request.get('cn', '')})
    
    @button.buttonAndHandler(_(u'Upload'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            return
        config = get_properties(self.context)
        storage = config['photo_storage']
        mutator = getattr(self, 'setPhoto_'+storage)
        mutator(data)

    def setPhoto_ofs(self, data):
        photo_data = data['photo']
        content_type = self.widgets['photo'].value.headers['content-type']
        if content_type != 'image/jpeg':
            raise form.interfaces.WidgetActionExecutionError(
                   'photo', interface.Invalid(_(u'Is not a JPEG')))
        photo_file = StringIO()
        photo_file.write(photo_data)
        photo_id = str(data['uid'])
        ofs_image = Image(photo_id, 'photo for '+data['uid'],
                      photo_file, content_type='image/jpeg')
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        container = portal.portlet_contact_photo
        if photo_id in container: del container[photo_id]
        container[photo_id] = ofs_image
        IStatusMessage(self.request).addStatusMessage(
                                      _(u"The photo has been well upladed"))
        self.request.response.redirect(self.context.absolute_url()+'/view')

    def setPhoto_archetypes(self, data):
        raise NotImplementedError

    def setPhoto_ldap(self, data):
        photo = data['photo']
        #check the content type of the uploaded file
        content_type = self.widgets['photo'].value.headers['content-type']
        if content_type != 'image/jpeg':
            raise form.interfaces.WidgetActionExecutionError(
                   'photo', interface.Invalid(_(u'Is not a JPEG')))
        #try to set the photo to the contact
        try:
            setPhoto(self.context, data['uid'], photo)
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
                                      _(u"The photo has been well upladed"))
        self.request.response.redirect(self.context.absolute_url()+'/view')

    def updateWidgets(self):
        super(Form, self).updateWidgets()
        self.widgets['uid'].mode = HIDDEN_MODE

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

def setPhoto(context, uid , photo):
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
