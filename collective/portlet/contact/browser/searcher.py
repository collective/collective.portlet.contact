# -*- coding: utf-8 -*-

from AccessControl import Unauthorized

from Products.Five import BrowserView
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName

from collective.portlet.contact.utils import getPortletContactUtility

class ContactSearchView(BrowserView):
    """ This browser view is just a bridge for the selected contact utility. """
  
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def search(self, q="", limit=10):
        """."""
        context = self.context
        # I don't know why permission="cmf.ManagePortal" doesn't works
        # in configure.zcml for this browser view.
        portal_membership = getToolByName(context, 'portal_membership')
        if portal_membership.checkPermission(ModifyPortalContent, context):
            utility = getPortletContactUtility(context)
            return utility.search(context, q=q, limit=limit)
        else:
            raise Unauthorized
