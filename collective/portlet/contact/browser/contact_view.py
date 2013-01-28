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

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        self.request.response.setHeader('X-Theme-Disabled', '1')
        uniq_id = self.context.contact_id
        book = IAddressBook(self.context)
        self.contact_info = book.getContactInfos(uniq_id)
