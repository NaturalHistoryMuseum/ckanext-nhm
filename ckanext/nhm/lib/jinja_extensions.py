#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import re

from jinja2 import nodes
from jinja2.ext import Extension

from ckanext.nhm.lib.taxonomy import find_author_split


class TaxonomyFormatExtension(Extension):
    """
    A custom Jinja2 tag for formatting scientific names in HTML.
    """

    tags = {'taxonomy'}
    # keyed on the format
    format_to_fields = {}
    # keyed on the field name
    field_to_formats = {}
    # just a list of field names
    parsed_fields = []
    # common string formats
    common_strings = {
        'italics': '<em>{0}</em>',
        'bold': '<b>{0}</b>',
        'deitalicise': '<span style="font-style: normal;">{0}</span>',
    }

    def parse(self, parser):
        '''The main function of the tag - mostly Jinja2 logic.

        :param parser:

        :returns: the HTML-formatted body of the tag

        '''
        lineno = next(parser.stream).lineno

        args = [parser.parse_expression()]
        parser.stream.skip_if('comma')
        args.append(parser.parse_expression())
        parser.stream.skip_if('comma')
        args.append(parser.parse_expression())

        body = parser.parse_statements(['name:endtaxonomy'], drop_needle=True)
        return nodes.CallBlock(
            self.call_method('_reformat', args), [], [], body
        ).set_lineno(lineno)

    def _reformat(self, field_name, collection_code, record_dict, caller):
        """
        Controls the reformatting of the tag body.

        :param field_name: the name of the field whose value is being parsed currently,
                            e.g. 'specificEpithet' or 'genus'
        :param collection_code: the code for the collection this record belongs to
                                (for collection-specific rules)
        :param record_dict: the full record
        :param caller: the tag body

        :returns: HTML-formatted tag body
        """
        body = str(caller())

        # add any globals here, e.g. if every collection should have the
        # species italicised
        global_formatted_fields = {}
        global_parsed_fields = []

        collections = {
            '(?i)zoo': self._zoo,
            '(?i)bmnh\(e\)': self._ent,
            '(?i)pal': self._pal,
            '(?i)bot': self._bot,
            '(?i)min': self._min,
        }

        # get collection-specific rules
        if collection_code:
            for rgx, p in collections.items():
                if re.match(rgx, collection_code):
                    collection_formatted_fields, collection_parsed_fields = p
                    self.format_to_fields = self._merge(
                        global_formatted_fields, collection_formatted_fields
                    )
                    self.parsed_fields = global_parsed_fields + collection_parsed_fields
                    break

        self.field_to_formats = {
            f: [k for k, v in self.format_to_fields.items() if f in v]
            for f in set(
                [
                    item
                    for field_names in self.format_to_fields.values()
                    for item in field_names
                ]
            )
        }

        for f, keys in self.format_to_fields.items():
            if field_name in keys:
                body = f(body)

        if field_name in self.parsed_fields:
            body = self._parse_field(body, record_dict)

        return body

    @staticmethod
    def _merge(ff1, ff2):
        """
        Helper method to merge two lists of field formats.

        :param ff1: a dict where the keys are functions taking and outputting a single
                    string, and the values are the names of fields to which that
                    function should be applied
        :type ff1: <function, string[]> dict
        :param ff2: a dict where the keys are functions taking and outputting a single
                    string, and the values are the names of fields to which that
                    function should be applied
        :type ff2: <function, string[]> dict
        :returns: a combined dict
        """
        return {
            k: list(set(ff1.get(k, []) + ff2.get(k, []))) for k in set(ff1).union(ff2)
        }

    @property
    def _zoo(self):
        """
        Zoology-specific rules.

        :returns: a tuple of collections; a dictionary of string formatting functions
                  and corresponding field names, and a list of fields to be parsed
        """
        formatted_fields = {
            self.common_strings['italics'].format: [
                'specificEpithet',
                'genus',
                'subgenus',
            ],
            str.lower: ['specificEpithet', 'infraspecificEpithet'],
        }
        parsed_fields = [
            'scientificName',
            'infraspecificEpithet',
            'determinations Names',
        ]
        return formatted_fields, parsed_fields

    @property
    def _ent(self):
        """
        Entomology-specific rules. Will almost always follow zoology rules but can
        override them if necessary.

        :returns: a tuple of collections; a dictionary of string formatting functions
                  and corresponding field names, and a list of fields to be parsed
        """
        return self._zoo

    @property
    def _pal(self):
        """
        Palaeontology-specific rules. Will almost always follow zoology rules but can
        override them if necessary.

        :returns: a tuple of collections; a dictionary of string formatting functions
                  and corresponding field names, and a list of fields to be parsed
        """
        return self._zoo

    @property
    def _bot(self):
        """
        Botany-specific rules.

        :returns: a tuple of collections; a dictionary of string formatting functions
                  and corresponding field names, and a list of fields to be parsed
        """
        formatted_fields = {
            self.common_strings['italics'].format: [
                'specificEpithet',
                'genus',
                'subgenus',
            ],
            str.lower: ['specificEpithet', 'infraspecificEpithet'],
        }
        parsed_fields = [
            'scientificName',
            'infraspecificEpithet',
            'determinations Names',
        ]
        return formatted_fields, parsed_fields

    @property
    def _min(self):
        """
        Mineralogy-specific rules.

        :returns: a tuple of collections; a dictionary of string formatting functions
                  and corresponding field names, and a list of fields to be parsed
        """
        formatted_fields = {}
        parsed_fields = []
        return formatted_fields, parsed_fields

    def _parse_field(self, body, record_dict):
        """
        For longer/more complex fields with multiple parts that need to be variably
        italicised/not italicised. Mostly achieved via regex.

        :param body: the tag body
        :param record_dict: the full record

        :returns: the tag body wrapped in italics tags, with certain parts deitalicised
                  by wrapping in span tags
        """
        # abbreviations should not be italicised
        abbr = ['var', 'subsp', 'subvar', 'f', 'subf', 'ssp', 'cv']
        for a in abbr:
            body = re.sub(
                '(\s?{0}\.?\s)'.format(a),
                '<span style="font-style: normal;">\\1</span>',
                body,
            )

        # neither should authors
        body = self._find_authors(body, record_dict)

        return self.common_strings['italics'].format(body)

    def _find_authors(self, body, record_dict):
        """
        For finding authors in a parsed string.

        :param body: the tag body
        :param record_dict: the full record

        :returns: the tag body with the authors wrapped in deitalicising tags
        """
        ix = find_author_split(body, record_dict)
        if ix:
            authors = body[ix:]
            return f'{body[:ix]}' + self.common_strings["deitalicise"].format(authors)
        else:
            return body
