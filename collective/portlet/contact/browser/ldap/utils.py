# -*- coding: utf-8 -*-

import ldap

class LdapServer(object):

    def __init__(self, host, port, dn, credential, base, scope):
        self.l = None
        self.host = host
        self.port = port
        self.dn = dn
        self.credential = credential
        self.base = base
        self.scope = scope

    def connect(self):
        try:
            self.l = ldap.initialize('ldap://%s:%s' % (self.host, str(self.port)))
            self.l.simple_bind_s(self.dn, self.credential)
        except ldap.LDAPError, error_message:
            # Couldn't connect
            self.l = None

    def close(self):
        self.l.unbind_s()

    def is_connected(self):
        return self.l is not None

    def search(self, filter_key, term, attrs=None):
        filter = "%s=*%s*" % (filter_key, term)
        res = []

        try:
            entries = self.l.search_s(self.base, self.scope, 
                                      filter, attrlist=None)

            for entry in entries:
                
                ldap_path, contact = entry[0], entry[1]
                
                _attrs = attrs
                if attrs is None:
                    # return all attributes
                    _attrs = contact.keys()
                
                d = {}
                for attr in _attrs:
                    value = contact.get(attr, [None])
                    d[attr] = value[0]

                res.append({'path': ldap_path, 'datas': d})

        except ldap.LDAPError, error_message:
            print error_message

        return res