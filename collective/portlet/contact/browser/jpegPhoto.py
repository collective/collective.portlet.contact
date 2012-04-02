from collective.portlet.contact.interfaces import IPortletContactUtility
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

def get_properties(context):
    props = getPropertySheet(context)
    config = {}
    # Default photo path in the ZMI, used when the contact photo is not found.
    config['default_photo_path'] = getattr(props, 'ldap_default_photo_path','')
    # Photo storage backend: ldap, ofs or archetypes (archetypes backend is not yet implemented).
    config['photo_storage'] = getattr(props, 'ldap_photo_storage', 'ofs')
    # Used by the ofs backend, a path which point on an existing Plone folder.
    config['photo_ofs_directory'] = getattr(props, 'ldap_photo_ofs_directory', 'images')
    # For caching purpose, used by the Cache-Control max-age request header.
    config['photo_cache_maxage'] = getattr(props, 'ldap_photo_cache_maxage', '')
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
        self.request.response.setHeader('Content-Length', len(data))
        maxage = config['photo_cache_maxage']
        if maxage:
            self.request.response.setHeader('Cache-Control','max-age=%s'%maxage)
        self.request.response.write(data)


    def getFrom_ofs(self, uid):
        data = ''
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        config = get_properties(self.context)
        try:
            photo = portal.unrestrictedTraverse(config['photo_ofs_directory'] + '/' + uid)
        except AttributeError:
            photo = None
        except KeyError:
            photo = None

        if photo:
            data = str(photo.data)
        return data

    def getFrom_archetypes(self, uid):
        raise NotImplementedError

    def getFrom_default(self, uid):
        config = get_properties(self.context)
        default_path = config['default_photo_path']
        
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        try:
            image = portal.unrestrictedTraverse(default_path)
            data = image.data
        except AttributeError:
            self.context.plone_log('No valid default photo provided for collective.portlet.contact > LDAP backend')
            data = ''
        except KeyError:
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
                   'photo', interface.Invalid(_(u'Is not a JPEG photo')))
        photo_file = StringIO()
        photo_file.write(photo_data)
        photo_id = str(data['uid'])
        ofs_image = Image(photo_id, 'Photo for '+data['uid'],
                      photo_file, content_type='image/jpeg')
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        config = get_properties(self.context)
        try:
            container = portal.unrestrictedTraverse(config['photo_ofs_directory'])
        except AttributeError:
            self.context.plone_log('No valid Plone folder provided for collective.portlet.contact > LDAP backend & OFS backend for the photo')
            container = None
        except KeyError:
            self.context.plone_log('No valid Plone folder provided for collective.portlet.contact > LDAP backend & OFS backend for the photo')
            container = None
        
        if container:
            container = portal.portlet_contact_photo
            if photo_id in container: del container[photo_id]
            container[photo_id] = ofs_image
            IStatusMessage(self.request).addStatusMessage(
                                          _(u"The photo has been well uploaded"))
        else:
            IStatusMessage(self.request).addStatusMessage(
                                          _(u"The photo can't be uploaded"))
            
        self.request.response.redirect(self.context.absolute_url()+'/view')

    def setPhoto_archetypes(self, data):
        raise NotImplementedError

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
