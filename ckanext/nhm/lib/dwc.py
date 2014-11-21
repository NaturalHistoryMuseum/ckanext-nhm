#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
from lxml import etree
from collections import OrderedDict
import re


class DwC(object):
    """
    Parse dwcterms XSD

    Creates two OrderedDicts, one containing terms, the other groups
    We need to be able to access DwC definitions by term

    """

    # All DwC terms
    terms = OrderedDict()

    term_uris = {}

    def __init__(self, **kwargs):

        # Read the DwC terms XSD to populate terms and groups
        f = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'tdwg_dwcterms.xsd')

        data = etree.parse(open(f), etree.XMLParser())
        root = data.getroot()

        for group in root.iterfind("xs:group", namespaces=root.nsmap):

            group_label = self._group_label(group.get('name'))

            # Create a list for the group terms
            group_terms = OrderedDict()

            for term in group.iterfind("xs:sequence/xs:element", namespaces=root.nsmap):

                ns, name = term.get("ref").split(':')

                self.term_uris[name] = '{ns}{name}'.format(ns=root.nsmap[ns], name=name)

                # # Add to terms dictionary
                # self.terms[name] = {
                #     'group': group_label,
                #     'uri': '{ns}{name}'.format(ns=root.nsmap[ns], name=name),
                # }

                # Add to group terms
                group_terms[name] = self._field_label(name)

            # If we have terms for this group, add the group
            # We don't want empty groups
            if group_terms:
                self.terms[group_label] = group_terms



        # # Read the DwC terms XSD to populate terms and groups
        # f = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'tdwg_dwcterms.xsd')
        #
        # data = etree.parse(open(f), etree.XMLParser())
        # root = data.getroot()
        #
        # for group in root.iterfind("xs:group", namespaces=root.nsmap):
        #
        #     group_label = self.get_group_label(group.get('name'))
        #
        #     # Create a list for the group terms
        #     group_terms = []
        #
        #     for term in group.iterfind("xs:sequence/xs:element", namespaces=root.nsmap):
        #
        #         ns, name = term.get("ref").split(':')
        #
        #         try:
        #             value = kwargs.pop(name)
        #         except KeyError:
        #             # If the value doesn't exist in kwargs, we don't care, it won't get added to __dict__
        #             pass
        #         else:
        #
        #             # Add to terms dictionary
        #             self.terms[name] = {
        #                 'group': group_label,
        #                 'uri': '{ns}{name}'.format(ns=root.nsmap[ns], name=name),
        #                 'value': value
        #             }
        #
        #             # Add to group terms
        #             group_terms.append(name)
        #
        #     # If we have terms for this group, add the group
        #     # We don't want empty groups
        #     if group_terms:
        #         self.groups[group_label] = group_terms
        #
        # # Created isn't part of the DwC standard, but add as Dublin Core
        # self.terms['created'] = {
        #     'group': self.terms['modified']['group'],
        #     'uri': self.terms['modified']['uri'].replace('modified', 'created'),
        #     'value': kwargs.pop('created')
        # }
        #
        # # Do we have any kwargs left (excluding hidden fields)
        # unknown_terms = [k for k in kwargs if not k.startswith('_')]
        # if unknown_terms:
        #     # If we do, they do not match any known DwC fields - so raise an error
        #     raise ValueError('Unknown DwC term: %s' % ','.join(unknown_terms))
        # self.parse_terms()

    # def parse_terms(self):
    #     """
    #     Parse the DwC terms file
    #     @return:
    #     """



    @staticmethod
    def _group_label(group_name):
        """
        Get a label for the group
        Takes the original group name, removes Term, de-pluralises and splits on capital
        GeologicalContextsTerm => Geological Contexts
        @param group: Original group name
        @return: label
        """
        label = ' '.join(re.findall('[A-Z][a-z]*', group_name.replace('Term', '')))

        if label.endswith('s'):
            label = label[:-1]

        return label

    @staticmethod
    def _field_label(field):

        label = re.sub('([A-Z]+)', r' \1', field).capitalize()
        label = label.replace(' id', ' ID')
        return label

    def get_groups(self):
        """
        @return: Generator of group names
        """
        for group, terms in self.groups.items():
            yield group, terms

    def get_term(self, name):
        """
        Get a term by name
        @param name:
        @return: term obj
        """
        return self.terms[name]


