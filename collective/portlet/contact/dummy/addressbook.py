# -*- coding: utf-8 -*-

from zope import interface
from zope import component
from Products.CMFCore.utils import getToolByName

from collective.portlet.contact.utils import encode_email
from collective.portlet.contact.addressbook import IAddressBook


class DummyAddressBook(object):
    interface.implements(IAddressBook)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.properties = None
        self.context = context

    def update(self):
        if self.properties is None:
            name = 'portal_properties'
            portal_properties = getToolByName(self.context, name)
            self.properties = portal_properties.portlet_contact_properties

    def search(self, q="", limit=10):
        # Used by the autocomplete widget
        self.update()
        props = self.properties
        item_str = "%(fullname)s - %(mail)s|%(id)s"
        contact = item_str % {
            'fullname': props.dummy_fullname,
            'mail': props.dummy_mail,
            'id': 'uniq_id'
        }
        if q in contact.lower():
            return [contact][:int(limit)]
        return []

    def getContactInfos(self, uniq_id):
        # Used by the portlet
        if uniq_id != 'uniq_id':
            return None
        self.update()
        props = self.properties
        return {'fullname': props.dummy_fullname,
                'phonenumber': props.dummy_phone,
                'mail': encode_email(props.dummy_mail,
                                     props.dummy_mail),
                'employeetype': props.dummy_employee_type,
                'photourl': props.dummy_photo_url}
