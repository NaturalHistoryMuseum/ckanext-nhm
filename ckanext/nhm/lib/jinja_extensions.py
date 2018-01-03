# coding=utf-8

from jinja2.ext import Extension
from jinja2 import nodes
import re
import abc
from collections import OrderedDict


class TaxonomyFormatExtension(Extension):
    '''
    A custom Jinja2 tag for formatting scientific names in HTML.
    '''
    tags = {'taxonomy'}
    # keyed on the format
    format_to_fields = {}
    # keyed on the field name
    field_to_formats = {}
    # just a list of field names
    parsed_fields = []
    # common string formats
    common_strings = {
        'italics': u'<em>{0}</em>',
        'bold': u'<b>{0}</b>',
        'deitalicise': u'<span style="font-style: normal;">{0}</span>'}

    def parse(self, parser):
        '''
        The main function of the tag - mostly Jinja2 logic.
        :param parser:
        :return: The HTML-formatted body of the tag.
        '''
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
        '''
        Controls the reformatting of the tag body.
        :param field_name: the name of the field whose value is being parsed currently, e.g. 'specificEpithet' or 'genus'
        :param collection_code: the code for the collection this record belongs to (for collection-specific rules)
        :param record_dict: the full record
        :param caller: the tag body
        :return: HTML-formatted tag body
        '''
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
        if collection_code:
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
        '''
        Helper method to merge two lists of field formats.
        :param ff1: <function, string> dict (function must take 1 string arg)
        :param ff2: <function, string> dict (function must take 1 string arg)
        :return: a combined dict
        '''
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
        parsed_fields = ['scientificName', 'infraspecificEpithet', 'determinations Names']
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
        parsed_fields = ['scientificName', 'infraspecificEpithet', 'determinations Names']
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
        '''
        For longer/more complex fields with multiple parts that need to be variably italicised/not italicised. Mostly achieved via regex.
        :param body: the tag body
        :param record_dict: the full record
        :return: the tag body wrapped in italics tags, with certain parts deitalicised by wrapping in span tags
        '''
        # abbreviations should not be italicised
        abbr = [u'var', u'subsp', u'subvar', u'f', u'subf', u'ssp', u'cv']
        for a in abbr:
            body = re.sub(u'(\s?{0}\.?\s)'.format(a),
                          u'<span style="font-style: normal;">\\1</span>',
                          body)

        # neither should authors
        body = self._find_authors(body, record_dict)

        return self.common_strings['italics'].format(body)

    def _find_authors(self, body, record_dict):
        '''
        For finding authors in a parsed string.
        :param body: the tag body
        :param record_dict: the full record
        :return: the tag body with the authors wrapped in deitalicising tags
        '''
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
            return u'{0}'.format(body[:ix]) + self.common_strings[
                'deitalicise'].format(authors)
        else:
            return body


class BaseParserStage(object):
    '''
    Represents a single stage of a field parsing process.
    '''
    @abc.abstractmethod
    def _meets_criteria(self, body, record_dict):
        '''
        Tests to see if the item meets certain criteria.
        :param body: the tag body to search in
        :param record_dict: the full record
        :return: boolean for pass/fail
        '''
        return True

    @abc.abstractmethod
    def _extract(self, body, record_dict):
        '''
        Finds an index within a string
        :param body: the tag body
        :param record_dict: the full record
        :return: a character index
        '''
        return 0

    def evaluate(self, body, record_dict):
        '''
        Checks if the item meets the criteria then returns the index
        :param body: the tag body
        :param record_dict: the full record
        :return: character index if criteria met, None if not
        '''
        if self._meets_criteria(body, record_dict):
            return self._extract(body, record_dict)


class AuthorParserStage(BaseParserStage):
    '''
    A specific stage for searching for authors in the tag body.
    '''
    def _meets_criteria(self, body, record_dict):
        '''
        Ensures an author field is present in the record.
        '''
        return 'scientificNameAuthorship' in record_dict.keys()

    def _extract(self, body, record_dict):
        '''
        Searches for the full author string, then breaks it up into smaller pieces (sections in brackets, individual names) if that's not found
        :return: the start index of the author string if found, otherwise None
        '''
        full_author = record_dict['scientificNameAuthorship']
        author_strings = [full_author] + [p.strip() for p in set(
                re.findall(u'\(([\w\s]+)\)', full_author) + re.findall(
                        u'([\w.\s]+)', full_author))]
        for a in author_strings:
            matches = re.search(u'\s\(?{0}\)?(\s|$)'.format(re.escape(a)), body)
            return matches.start() if matches else None


class SimpleFieldParserStage(BaseParserStage):
    '''
    A generic stage for searching for a certain field within the tag body (for the purposes of finding authors).
    '''
    def __init__(self, field_name):
        self.field_name = field_name

    def _meets_criteria(self, body, record_dict):
        '''
        Checks that the record contains a value for this field and that the value is present in the tag body.
        '''
        return self.field_name in record_dict.keys() and record_dict[
                                                             self.field_name] in body

    def _extract(self, body, record_dict):
        '''
        If the value is at the end of the string, there is no point in continuing; otherwise, it looks for the first capitalised word after that value.
        :return: the start index of the estimated author string if found, else None.
        '''
        field_value = record_dict[self.field_name]
        if re.search('{0}$'.format(re.escape(field_value)), body):
            return len(body)
        split_by_value = re.split('{0}'.format(re.escape(field_value)), body,
                                  1)
        matches = re.search('\(?[A-Z]\w*', split_by_value[1])
        return matches.start() + len(split_by_value[0]) + len(
                field_value) if matches else None


class CapitalisedParserStage(BaseParserStage):
    '''
    The last resort stage in the search for authors - searches for the second capitalised word in the tag body.
    '''
    def _meets_criteria(self, body, record_dict):
        '''
        Checks for multiple capitalised words in the tag body.
        '''
        capit = re.findall('([A-Z]\S*)(?:\s|$)', body)
        return len(capit) > 1

    def _extract(self, body, record_dict):
        '''
        Finds the start index of the second capitalised word.
        '''
        matches = [m for m in re.finditer('[A-Z]', body)]
        return matches[1].start()
