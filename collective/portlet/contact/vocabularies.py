# -*- coding: utf-8 -*-

from zope.component import getUtilitiesFor
from zope.interface import classProvides
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from collective.portlet.contact.interfaces import IPortletContactUtility

class PortletContactUtilities(SimpleVocabulary):
    """A vocabulary containing portlet contact utility names."""
    
    classProvides(IVocabularyFactory)
    
    def __init__(self, context):
        terms = []
        utilities = getUtilitiesFor(IPortletContactUtility)
        for name, utility in utilities:
            terms.append(SimpleTerm(name, name, name))
        super(PortletContactUtilities, self).__init__(terms)
