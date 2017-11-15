# coding=utf-8

from jinja2.ext import Extension
from jinja2 import nodes
import re
import abc
from collections import OrderedDict


class TaxonomyFormatExtension(Extension):
    tags = set(['taxonomy'])
    # keyed on the format
    format_to_fields = {}
    # keyed on the field name
    field_to_formats = {}
    # just a list of field names
    parsed_fields = []
    # common string formats
    common_strings = {'italics': u'<em>{0}</em>', 'bold': u'<b>{0}</b>', 'deitalicise': u'<span style="font-style: normal;">{0}</span>'}

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = [parser.parse_expression()]
        parser.stream.skip_if('comma')
        args.append(parser.parse_expression())
        parser.stream.skip_if('comma')
        args.append(parser.parse_expression())

        body = parser.parse_statements(['name:endtaxonomy'],
                                       drop_needle = True)
        return nodes.CallBlock(self.call_method('_reformat', args), [], [],
                               body).set_lineno(lineno)

    def _reformat(self, field_name, collection_code, record_dict, caller):
        body = unicode(caller())

        # add any globals here, e.g. if every collection should have the
        # species italicised
        global_formatted_fields = {}
        global_parsed_fields = []

        collections = {
            '(?i)zoo': self._zoo,
            '(?i)bmnh\(e\)': self._ent,
            '(?i)pal': self._pal,
            '(?i)bot': self._bot,
            '(?i)min': self._min, }

        # get collection-specific rules
        for rgx, p in collections.items():
            if re.match(rgx, collection_code):
                collection_formatted_fields, collection_parsed_fields = p
                self.format_to_fields = self._merge(global_formatted_fields,
                                                    collection_formatted_fields)
                self.parsed_fields = global_parsed_fields + \
                                     collection_parsed_fields
                break

        self.field_to_formats = {
            f: [k for k, v in self.format_to_fields.items() if f in v] for f in
            set([item for field_names in self.format_to_fields.values() for
                 item in field_names])}

        for f, keys in self.format_to_fields.items():
            if field_name in keys:
                body = f(body)

        if field_name in self.parsed_fields:
            body = self._parse_field(body, record_dict)

        return body

    @staticmethod
    def _merge(ff1, ff2):
        return {k: list(set(ff1.get(k, []) + ff2.get(k, []))) for k in
                set(ff1.keys() + ff2.keys())}

    @property
    def _zoo(self):
        '''
        Zoology-specific rules.
        :return:
        '''
        formatted_fields = {
            self.common_strings['italics'].format: ['specificEpithet', 'genus',
                                                    'subgenus'],
            unicode.lower: ['specificEpithet', 'infraspecificEpithet']}
        parsed_fields = ['scientificName', 'infraspecificEpithet']
        return formatted_fields, parsed_fields

    @property
    def _ent(self):
        '''
        Entomology-specific rules. Will almost always follow zoology rules but
        can override them if necessary.
        :return:
        '''
        return self._zoo

    @property
    def _pal(self):
        '''
        Palaeontology-specific rules. Will almost always follow zoology rules
        but can override them if necessary.
        :return:
        '''
        return self._zoo

    @property
    def _bot(self):
        '''
        Botany-specific rules.
        :return:
        '''
        formatted_fields = {
            self.common_strings['italics'].format: ['specificEpithet', 'genus',
                                                    'subgenus'],
            unicode.lower: ['specificEpithet', 'infraspecificEpithet']}
        parsed_fields = ['scientificName', 'infraspecificEpithet']
        return formatted_fields, parsed_fields

    @property
    def _min(self):
        '''
        Mineralogy-specific rules.
        :return:
        '''
        formatted_fields = {}
        parsed_fields = []
        return formatted_fields, parsed_fields

    def _parse_field(self, body, record_dict):
        # abbreviations should not be italicised
        abbr = [u'var', u'subsp', u'subvar', u'f', u'subf', u'ssp', u'cv']
        for a in abbr:
            body = re.sub(u'(\s?{0}\.?\s)'.format(a), u'<span style="font-style: normal;">\\1</span>', body)

        # neither should authors
        body = self._find_authors(body, record_dict)

        return self.common_strings['italics'].format(body)

    def _find_authors(self, body, record_dict):
        # if it's just a single word, no need to parse
        first_space = re.search('\s', body)
        if not first_space:
            return body

        evaluators = OrderedDict()
        evaluators['authors'] = AuthorParserStage()
        evaluators['species'] = SimpleFieldParserStage('specificEpithet')
        evaluators['subgenus'] = SimpleFieldParserStage('subgenus')
        evaluators['capitalisation'] = CapitalisedParserStage()

        ix = None
        for t, e in evaluators.items():
            ix = e.evaluate(body, record_dict)
            if ix:
                break

        if ix:
            authors = body[ix:]
            return u'{0}'.format(body[:ix]) + self.common_strings['deitalicise'].format(authors)
        else:
            return body


class BaseParserStage(object):
    @abc.abstractmethod
    def _meets_criteria(self, body, record_dict):
        return True

    @abc.abstractmethod
    def _extract(self, body, record_dict):
        return 0

    def evaluate(self, body, record_dict):
        if self._meets_criteria(body, record_dict):
            return self._extract(body, record_dict)


class AuthorParserStage(BaseParserStage):
    def _meets_criteria(self, body, record_dict):
        return 'scientificNameAuthorship' in record_dict.keys()

    def _extract(self, body, record_dict):
        full_author = record_dict['scientificNameAuthorship']
        author_strings = [full_author] + [p.strip() for p in set(
                re.findall('\(([\w\s]+)\)', full_author) + re.findall(
                        '([\w.\s]+)', full_author))]
        for a in author_strings:
            matches = re.search('\s\(?{0}\)?(\s|$)'.format(re.escape(a)), body)
            return matches.start() if matches else None


class SimpleFieldParserStage(BaseParserStage):
    def __init__(self, field_name):
        self.field_name = field_name

    def _meets_criteria(self, body, record_dict):
        return self.field_name in record_dict.keys() and record_dict[
                                                             self.field_name] in body

    def _extract(self, body, record_dict):
        field_value = record_dict[self.field_name]
        if re.search('{0}$'.format(re.escape(field_value)), body):
            return len(body)
        split_by_value = re.split('{0}'.format(re.escape(field_value)), body,
                                  1)
        matches = re.search('\(?[A-Z]\w*', split_by_value[1])
        return matches.start() + len(split_by_value[0]) + len(
            field_value) if matches else None


class CapitalisedParserStage(BaseParserStage):
    def _meets_criteria(self, body, record_dict):
        capit = re.findall('[\s(]([A-Z]\S*)(?:\s|$)', body)
        return len(capit) >= 1

    def _extract(self, body, record_dict):
        matches = re.search('\s\(?[A-Z]', body)
        return matches.start()

    def evaluate(self, body, record_dict):
        if self._meets_criteria(body, record_dict):
            return self._extract(body, record_dict)
        else:
            return len(body)
