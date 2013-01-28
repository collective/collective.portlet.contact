# -*- coding: utf-8 -*-

from AccessControl import Unauthorized

from Products.Five import BrowserView
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from collective.portlet.contact.addressbook import IAddressBook


class ContactSearchView(BrowserView):
    """ This browser view is just a bridge for the selected contact utility.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def search(self, q="", limit=10):
        """."""
        # I don't know why permission="cmf.ManagePortal" doesn't works
        # in configure.zcml for this browser view.
        portal_membership = getToolByName(self.context, 'portal_membership')
        hasPermission = portal_membership.checkPermission
        if hasPermission(ModifyPortalContent, self.context):
            book = IAddressBook(self.context)
            return book.search(q=q, limit=limit)
        else:
            raise Unauthorized
