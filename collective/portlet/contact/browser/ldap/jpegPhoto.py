from collective.portlet.contact.interfaces import IPortletContactUtility
from collective.portlet.contact.browser.ldap import utils
from collective.portlet.contact.i18n import MessageFactory as _
import ldap

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.z3cform import layout
from zope import interface
from zope import schema
from zope.component import getUtility
from z3c.form import button, field, form
from z3c.form.interfaces import HIDDEN_MODE


class jpegPhoto(BrowserView):
    """return the jpeg photo get from uid"""
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        request = self.request
        uid = request.get('uid', None)
        if not uid:
            return ''

        utility = getUtility(IPortletContactUtility, name='ldap')

        entries = utility._search(self.context, search_on='uid',
                        attrs=['jpegPhoto'],
                        query=uid)

        if len(entries)<1:
            return ''

        data = entries[0]['datas']['jpegPhoto']
        if not data:
            return ''
        self.request.response.setHeader('Content-Type', 'image/jpeg')
        self.request.response.write(data)


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
        photo = data['photo']
        #check the content type of the uploaded file
        content_type = self.widgets['photo'].value.headers['content-type']
        if content_type != 'image/jpeg':
            raise form.interfaces.WidgetActionExecutionError(
                   'photo', interface.Invalid(_(u'Is not a JPEG')))
        config = self.getLDAPConfig()
        dn = 'uid=%s,%s'%(data['uid'], config['basedn'])
        #try to set the photo to the contact
        try:
            utils.setPhoto(dn, photo, config)
        except utils.ldap.SERVER_DOWN:
            raise form.interfaces.ActionExecutionError(
                    interface.Invalid(
                    _("The LDAP server is unreacheable")))
        except utils.ldap.INVALID_CREDENTIALS:
            raise form.interfaces.ActionExecutionError(
                    interface.Invalid(
                    _("The LDAP authentication credentials are invalid")))
        except utils.ldap.NO_SUCH_OBJECT:
            raise form.interfaces.ActionExecutionError(
                    interface.Invalid(
                    _("The entry you have specified is not in the LDAP")))

        IStatusMessage(self.request).addStatusMessage(
                                      _(u"The photo has been well upladed"))
        self.request.response.redirect(self.context.absolute_url()+'/view')

    def updateWidgets(self):
        super(Form, self).updateWidgets()
        self.widgets['uid'].mode = HIDDEN_MODE

    def getLDAPConfig(self):
        config = {}
        pp = getPropertySheet(context)
        config['server'] = '%s:%s'%(pp.ldap_server_host,pp.ldap_server_port)
        config['user'] = pp.ldap_bind_dn
        config['password'] = pp.ldap_bind_password
        config['basedn'] = pp.ldap_bind_password

        return config

class Page(layout.FormWrapper):

    form = Form

def setPhoto(dn, photo, ldapconfig):
    server = ldap.initialize(ldapconfig['server']) #'ldap://ldapmaster.makina-corpus.net:389')
    user = ldapconfig['user'] #"uid=jmf,ou=People,dc=mcjam,dc=org"
    pwd = ldapconfig['password']

    server.simple_bind_s(user, pwd)

    entry = server.search_s(dn, ldap.SCOPE_BASE)
    #get the photo:

    contact = entry[0][1]
    old_photo = contact.get('jpegPhoto')
    if old_photo:
        old_photo = old_photo[0]
    else:
        old_photo = ''
    old = {'jpegPhoto':old_photo}
    new = {'jpegPhoto':photo}

    ldif = modlist.modifyModlist(old,new)
    server.modify_s(user,ldif)

    server.unbind_s()
