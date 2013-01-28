import logging
from Products.Five.browser import BrowserView
from collective.portlet.contact.addressbook import IAddressBook

logger = logging.getLogger('collective.portlet.contact')


class ContactView(BrowserView):
    """Contact view"""

    def __init__(self, context, request):
        self.context = context  # portlet assignement
        self.request = request
        self.contact_info = {}
        self.book = None

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        self.request.response.setHeader('X-Theme-Disabled', '1')
        if self.book is None:
            self.book = IAddressBook(self.context)
        if not self.contact_info:
            uniq_id = self.context.contact_id
            self.contact_info = self.book.getContactInfos(uniq_id)
