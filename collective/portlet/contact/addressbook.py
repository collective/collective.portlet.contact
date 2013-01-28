from zope import interface
from zope import component
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from Products.CMFCore.utils import getToolByName


class IAddressBook(interface.Interface):
    """ An address book in read only mode let you search for contacts
    and get contact infos """

    def search(q="", limit=10):
        """ Search contacts from a user input string.
            * q: the search term
            * limit: max items returned
        """

    def getContactInfos(uniq_id):
        """ Return informations (dict) on the contact pointed by uniq_id.
            * uniq_id: a value which allows to retrieve the contact

            The dict must have the keys:
            * fullname
            * phonenumber
            * mail
            * employeetype
        """


class AddressBook(object):
    interface.implements(IAddressBook)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.context = context
        self.backend = None
        self.settings = None

    def update(self):
        if self.settings is None:
            properties = getToolByName(self.context, 'portal_properties')
            self.settings = properties.portlet_contact_properties

        if self.backend is None:
            name = self.settings.backend
            iface = IAddressBook
            self.backend = component.getAdapter(self.context, iface, name)

    def search(self, q="", limit=10):
        self.update()
        return self.backend.search(q=q, limit=limit)

    def getContactInfos(self, uniq_id):
        self.update()
        return self.backend.getContactInfos(uniq_id)


class AddressBooks(SimpleVocabulary):
    """A vocabulary containing portlet contact utility names."""

    interface.implements(IVocabularyFactory)

    def __init__(self, context):
        terms = []
        site = component.getSiteManager()
        books = list(component.getAdapters((site,), IAddressBook))
        for name, book in books:
            terms.append(SimpleTerm(name, name, unicode(name)))
        super(AddressBooks, self).__init__(terms)
