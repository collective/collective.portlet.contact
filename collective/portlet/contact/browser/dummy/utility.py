# -*- coding: utf-8 -*-

from zope.interface import implements, classProvides
from zope.component import adapts

from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.portlet.contact.interfaces import IPortletContactUtility
from collective.portlet.contact.utils import getPropertySheet, encode_email

class PortletContactDummy:
    classProvides(IPortletContactUtility)
    implements(IPortletContactUtility)
    
    def search(self, context, q="", limit=10):
        # Used by the autocomplete widget
        
        props = getPropertySheet(context)
        item_str = "%(fullname)s - %(mail)s|%(id)s"
        return item_str % {'fullname': props.dummy_fullname,
                           'mail': props.dummy_mail,
                           'id': 'uniq_id'}

    def getContactInfos(self, context, uniq_id):
        # Used by the portlet
        
        props = getPropertySheet(context)
        return {'fullname': props.dummy_fullname,
                'phonenumber': props.dummy_phone,
                'mail': encode_email(props.dummy_mail,
                                     props.dummy_mail),
                'employeetype': props.dummy_employee_type,
                'photourl': props.dummy_photo_url}

portletContactDummy = PortletContactDummy()