# -*- coding: utf-8 -*-

from zope.component import queryUtility

from Products.CMFCore.utils import getToolByName

from collective.portlet.contact.interfaces import IPortletContactUtility

def getPropertySheet(context):
    portal_properties = getToolByName(context, 'portal_properties')
    return getattr(portal_properties, 'portlet_contact_properties')

def getPortletContactUtilityName(context):
    """Return the selected contact utility name."""
    return getPropertySheet(context).backend

def getPortletContactUtility(context):
    """Return the selected contact utility."""
    return queryUtility(IPortletContactUtility, 
                        getPortletContactUtilityName(context))

# Tool to avoid spam on emails
# See http://www.zope.org/Members/jmeile/email_encoder

def hex_string(mystring):
    """ Use the powerfull python string formating
    """
    newstring=''
    length=len(mystring)
    for i in range(length):
        newstring+="%%%0.2X" % ord(mystring[i])
    return newstring

def encode_email(emailvalue, namevalue):
    #Taken from http://www.happysnax.com.au/testemail.php
    #Original comments:
    """this function creates the hexadecimal equivalent to "document.write('<a href="mailto:emailaddress">name</a>')"
       ie it effectively encrypts this as far as spam-bots are concerned
       the Javascript to unencrypt it simply changes the hex back into ascii
       then executes the code using the 'eval' statement
       /... and ta da ... you've got a normal mailto address displayed in the browser.
       //Written by Jeff Robson of Cynergic Net Solutions www.cynergic.net jeff.robson@cynergic.net"""
    if emailvalue is not None and namevalue is not None:
        new_text=hex_string('document.write(\'<a href=\"mailto:'+emailvalue+'\">'+namevalue+'</a>\')')
        return '<script language=\"JavaScript\">eval(unescape(\''+new_text+'\'))</script>'
    else:
        return ''
