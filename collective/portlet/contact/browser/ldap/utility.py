# -*- coding: utf-8 -*-

import ldap

from zope.interface import implements, classProvides
from zope.component import adapts

from Products.CMFPlone.interfaces import IPloneSiteRoot

from collective.portlet.contact.interfaces import IPortletContactUtility
from collective.portlet.contact.utils import getPropertySheet, encode_email
from collective.portlet.contact.browser.ldap.utils import LdapServer

class PortletContactLdap:
    classProvides(IPortletContactUtility)
    implements(IPortletContactUtility)
    
    def _search(self, context,
                      search_on='cn', 
                      query='', 
                      attrs=['uid', 'cn', 'mail'], 
                      limit=10):
        # connect to the LDAP server
        props = getPropertySheet(context)
        
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

    def search(self, context, q="", limit=10):
        # Used by the autocomplete widget
        
        contacts = self._search(context,
                                search_on='cn', 
                                query=q, 
                                attrs=['uid', 'cn', 'mail'], 
                                limit=limit)
        
        results = ['%s (%s)|%s' % (c['datas']['cn'], 
                                   c['datas']['mail'], 
                                   c['datas']['uid']) for c in contacts]
        
        return '\n'.join(results)

    def getContactInfos(self, context, uniq_id):
        # Used by the portlet
        
        contacts = self._search(context,
                                search_on='uid', 
                                query=uniq_id, 
                                attrs=['uid', 'cn', 'mail', 'telephoneNumber',
                                       'employeeType'], 
                                limit=1)
        if contacts:
            c = contacts[0]
            return {'fullname': c['datas']['cn'],
                    'phonenumber': c['datas']['telephoneNumber'],
                    'mail': encode_email(c['datas']['mail'],
                                         c['datas']['mail']),
                    'employeetype': c['datas']['employeeType']}
        else:
            return None
