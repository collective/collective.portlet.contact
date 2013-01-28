# -*- coding: utf-8 -*-

import ldap

from zope import interface
from zope import component
from Products.CMFCore.utils import getToolByName

from collective.portlet.contact.utils import encode_email
from collective.portlet.contact.browser.ldap.utils import LdapServer
from collective.portlet.contact.addressbook import IAddressBook


class LDAPAddressBook(object):
    interface.implements(IAddressBook)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.context = context

    def _search(self, search_on='cn', query='', attrs=None, limit=10):
        context = self.context
        if attrs is None:
            attrs = ['uid', 'cn', 'mail']
        # connect to the LDAP server
        portal_properties = getToolByName(context, 'portal_properties')
        props = getattr(portal_properties, 'portlet_contact_properties')

        if props.ldap_search_recursive:
            SCOPE = ldap.SCOPE_SUBTREE
        else:
            SCOPE = ldap.SCOPE_ONELEVEL

        server = LdapServer(props.ldap_server_host,
                            props.ldap_server_port,
                            props.ldap_bind_dn,
                            props.ldap_bind_password,
                            props.ldap_search_base,
                            SCOPE)
        server.connect()

        # search contacts
        results = []

        if server.is_connected():
            results = server.search(search_on, query, attrs=attrs)[:int(limit)]
            # close connection
            server.close()

        return results

    def search(self, q="", limit=10, search_on='cn', attrs=[], format='ajax'):
        # Used by the autocomplete widget
        attrs.extend(['uid', 'cn', 'mail'])
        search_attr = list(set(attrs))
        contacts = self._search(search_on=search_on,
                                query=q,
                                attrs=search_attr,
                                limit=limit)

        if format != 'ajax':
            return contacts

        results = []
        for c in contacts:
            if c['datas']['mail']:
                value = '%s (%s)' % (c['datas']['cn'],
                                     c['datas']['mail'])
            else:
                value = c['datas']['cn']
            uid = c['datas']['uid']
            results.append('%s|%s' % (value, uid))

        return '\n'.join(results)

    def getContactInfos(self, uniq_id):
        context = self.context
        # Used by the portlet
        urltool = getToolByName(context, 'portal_url')
        contacts = self._search(search_on='uid',
                                query=uniq_id,
                                attrs=['uid', 'cn', 'mail', 'telephoneNumber',
                                       'employeeType'],
                                limit=1)
        if contacts:
            c = contacts[0]
            uid = c['datas']['uid']
            path = '/@@collective_portlet_contact_photo?uid=' + uid
            jpegurl = urltool() + path
            return {'fullname': c['datas']['cn'],
                    'phonenumber': c['datas']['telephoneNumber'],
                    'mail': encode_email(c['datas']['mail'],
                                         c['datas']['mail']),
                    'employeetype': c['datas']['employeeType'],
                    'uid': c['datas']['uid'],
                    'photourl': jpegurl}
        else:
            return None

ldap_addressbook = LDAPAddressBook()
