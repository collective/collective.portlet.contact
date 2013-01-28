from collective.portlet.contact.i18n import MessageFactory as _

from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from plone.app.z3cform import layout
from zope import interface
from zope import schema
from z3c.form import button, field, form
from z3c.form.interfaces import HIDDEN_MODE
from OFS.Image import Image
from StringIO import StringIO


def get_properties(context):
    portal_properties = getToolByName(context, 'portal_properties')
    props = getattr(portal_properties, 'portlet_contact_properties')
    config = {}
    # Default photo path in the ZMI, used when the contact photo is not found.
    photo_path = getattr(props, 'ldap_default_photo_path', '')
    config['default_photo_path'] = photo_path
    # Photo storage backend: ldap, ofs or archetypes
    config['photo_storage'] = getattr(props, 'ldap_photo_storage', 'ofs')
    # Used by the ofs backend, a path which point on an existing Plone folder.
    directory = getattr(props, 'ldap_photo_ofs_directory', 'images')
    config['photo_ofs_directory'] = directory
    # For caching purpose, used by the Cache-Control max-age request header.
    maxage = getattr(props, 'ldap_photo_cache_maxage', '')
    config['photo_cache_maxage'] = maxage
    return config


class jpegPhoto(BrowserView):
    """return the jpeg photo get from uid
       or '' if an error occured (photo unavailable in LDAP and no default
       photo provided)"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.settings = None
        self.storage = None
        self.portal = None

    def update(self):
        if self.settings is None:
            self.settings = get_properties(self.context)
        if self.storage is None:
            self.storage = self.settings['photo_storage']
        if self.portal is None:
            urltool = getToolByName(self.context, 'portal_url')
            self.portal = urltool.getPortalObject()

    def getPhoto(self, uid):
        accessor = getattr(self, 'getFrom_' + self.storage)
        data = accessor(uid)
        if not data:
            data = self.getFrom_default(uid)
        return data

    def __call__(self):
        request = self.request
        uid = request.get('uid', None)
        if not uid:
            return ''
        self.update()
        data = self.getPhoto(uid)

        self.request.response.setHeader('Content-Type', 'image/jpeg')
        self.request.response.setHeader('Content-Length', len(data))
        maxage = self.settings['photo_cache_maxage']
        if maxage:
            maxage_str = 'max-age=%s' % maxage
            self.request.response.setHeader('Cache-Control', maxage_str)
        self.request.response.write(data)

    def getFrom_ofs(self, uid):
        data = ''
        config = self.settings
        try:
            path = config['photo_ofs_directory'] + '/' + uid
            photo = self.portal.unrestrictedTraverse(path)
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
        config = self.settings
        default_path = config['default_photo_path']

        try:
            image = self.portal.unrestrictedTraverse(default_path)
            data = image.data
        except AttributeError:
            msg = 'No valid default photo provided for'\
                'collective.portlet.contact > LDAP backend'
            self.context.plone_log(msg)
            data = ''
        except KeyError:
            msg = 'No valid default photo provided for '\
                'collective.portlet.contact > LDAP backend'
            self.context.plone_log(msg)
            data = ''
        return data


class Schema(interface.Interface):
    """Schema to upload a photo to contact inside LDAP"""

    photo = schema.Bytes(
        title=_(u'Photo'),
        description=_(u'Upload a jpeg photo.'),
        #max_length=800000
    )

    uid = schema.TextLine(
        title=_(u'Unique ID'),
        description=_(u'The unique ID of the ldap entry.'),
    )


class Form(form.Form):

    fields = field.Fields(Schema)
    ignoreContext = True

    @property
    def label(self):
        mapping = {'cn': self.request.get('cn', '')}
        return _(u"Contact\'s photo form ${cn}", mapping=mapping)

    @button.buttonAndHandler(_(u'Upload'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            return
        config = self.settings
        storage = config['photo_storage']
        mutator = getattr(self, 'setPhoto_' + storage)
        mutator(data)

    def setPhoto_ofs(self, data):
        photo_data = data['photo']
        content_type = self.widgets['photo'].value.headers['content-type']
        if content_type != 'image/jpeg':
            error = interface.Invalid(_(u'Is not a JPEG photo'))
            raise form.interfaces.WidgetActionExecutionError('photo', error)
        photo_file = StringIO()
        photo_file.write(photo_data)
        photo_id = str(data['uid'])
        ofs_image = Image(
            photo_id, 'Photo for ' + data['uid'],
            photo_file, content_type='image/jpeg'
        )
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        config = self.settings
        try:
            path = config['photo_ofs_directory']
            container = portal.unrestrictedTraverse(path)
        except AttributeError:
            msg = 'No valid Plone folder provided for'\
                'collective.portlet.contact > LDAP backend & '\
                'OFS backend for the photo'
            self.context.plone_log(msg)
            container = None
        except KeyError:
            msg = 'No valid Plone folder provided for '\
                'collective.portlet.contact > LDAP backend &'\
                'OFS backend for the photo'
            self.context.plone_log(msg)
            container = None

        if container:
            container = portal.portlet_contact_photo
            if photo_id in container:
                del container[photo_id]
            container[photo_id] = ofs_image
            msg = _(u"The photo has been well uploaded")
            IStatusMessage(self.request).addStatusMessage(msg)
        else:
            msg = _(u"The photo can't be uploaded")
            IStatusMessage(self.request).addStatusMessage(msg)

        url = self.context.absolute_url() + '/view'
        self.request.response.redirect(url)

    def setPhoto_archetypes(self, data):
        raise NotImplementedError

    def updateWidgets(self):
        super(Form, self).updateWidgets()
        self.widgets['uid'].mode = HIDDEN_MODE

    def update(self):
        super(Form, self).update()

        if not hasattr(self, 'settings'):
            self.settings = get_properties(self.context)

        if getattr(self, 'config', None):
            config = {}
            portal_properties = getToolByName(
                self.context, 'portal_properties'
            )
            pp = getattr(portal_properties, 'portlet_contact_properties')
            config['host'] = pp.ldap_server_host
            config['port'] = pp.ldap_server_port
            config['user'] = pp.ldap_bind_dn
            config['password'] = pp.ldap_bind_password
            config['basedn'] = pp.ldap_search_base
#            if pp.ldap_search_recursive:
#                config['scope'] = ldap.SCOPE_SUBTREE
#            else:
#                config['scope'] = ldap.SCOPE_ONELEVEL
            self.config = config


class Page(layout.FormWrapper):

    form = Form
