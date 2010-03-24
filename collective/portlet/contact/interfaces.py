# -*- coding: utf-8 -*-

from zope.interface import Interface

class IPortletContactUtility(Interface):
    """ Contact utility """

    def search(context, q="", limit=10):
        """ Search contacts from a user input string.
            * context: the current context
            * q: the search term
            * limit: max items returned
        """

    def getContactInfos(context, uniq_id):
        """ Return informations (dict) on the contact pointed by uniq_id.
            * context: the current context
            * uniq_id: a value which allows to retrieve the contact
            
            The dict must have the keys:
            * fullname
            * phonenumber
            * mail
            * employeetype
        """