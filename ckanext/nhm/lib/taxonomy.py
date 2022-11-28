#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import abc
import re
from collections import OrderedDict


def extract_ranks(record):
    """
    Extracts the values for each rank (if present) in the given record. Ranks missing
    from the record are not omitted.

    :param record: the record dict
    :return: the ranks as an OrderedDict in rank order.
    """
    ranks = [
        ('kingdom', extract_kingdom),
        ('phylum', extract_phylum),
        ('class', extract_class),
        ('family', extract_family),
        ('genus', extract_genus),
        ('species', extract_species),
    ]
    # extract all the rank values
    extracted_ranks = [(rank, extractor(record)) for rank, extractor in ranks]
    # filter out the missing values and return as an OrderedDict
    return OrderedDict([(rank, value) for rank, value in extracted_ranks if value])


def extract_kingdom(record):
    """
    Extract the kingdom value from the given record.

    :param record: the record dict
    :return: the kingdom value, or None if it is not present
    """
    return record.get('kingdom', None)


def extract_phylum(record):
    """
    Extract the phylum value from the given record.

    :param record: the record dict
    :return: the phylum value, or None if it is not present
    """
    return record.get('phylum', None)


def extract_class(record):
    """
    Extract the class value from the given record.

    :param record: the record dict
    :return: the class value, or None if it is not present
    """
    return record.get('class', None)


def extract_family(record):
    """
    Extract the family value from the given record.

    :param record: the record dict
    :return: the family value, or None if it is not present
    """
    return record.get('family', None)


def extract_genus(record):
    """
    Extract the genus value from the given record.

    :param record: the record dict
    :return: the genus value, or None if it is not present
    """
    return record.get('genus', None)


def extract_species(record):
    """
    Extract the species value from the given record. This is achieved by extracting the
    species from the `scientificName` field of the record (if there is one) and the
    removal of any extra details (such as the author) from this value.

    :param record: the record dict
    :return: the species value, or None if it is not present
    """
    # try extracting the species from the scientific name, which starts with the species but often
    # has an author or date after it
    scientific_name = record.get('scientificName', None)
    if scientific_name:
        ix = find_author_split(scientific_name, record)
        return scientific_name[:ix].strip()

    return None


def find_author_split(value, record_dict):
    """
    Given a string and a record attempts to determine where in the string an author is
    defined. If an author is found then this will return the index the author part
    starts, otherwise returns None.

    :param value:           the value to search in
    :param record_dict:     the record dictionary to use as a supplementary source of information
    :return: the index at the start of the author part or None
    """
    first_space = re.search(r'\s', value)
    if not first_space:
        return None

    evaluators = [
        AuthorParserStage(),
        SimpleFieldParserStage('specificEpithet'),
        SimpleFieldParserStage('subgenus'),
        CapitalisedParserStage(),
    ]

    ix = None
    for evaluator in evaluators:
        ix = evaluator.evaluate(value, record_dict)
        if ix:
            break

    return ix


class BaseParserStage(object):
    """
    Represents a single stage of a field parsing process.
    """

    @abc.abstractmethod
    def _meets_criteria(self, body, record_dict):
        """
        Tests to see if the item meets certain criteria.

        :param body: the tag body to search in
        :param record_dict: the full record
        :return: boolean for pass/fail
        """
        return True

    @abc.abstractmethod
    def _extract(self, body, record_dict):
        """
        Finds an index within a string.

        :param body: the tag body
        :param record_dict: the full record
        :return: a character index
        """
        return 0

    def evaluate(self, body, record_dict):
        """
        Checks if the item meets the criteria then returns the index.

        :param body: the tag body
        :param record_dict: the full record
        :return: character index if criteria met, None if not
        """
        if self._meets_criteria(body, record_dict):
            return self._extract(body, record_dict)


class AuthorParserStage(BaseParserStage):
    """
    A specific stage for searching for authors in the tag body.
    """

    def _meets_criteria(self, body, record_dict):
        """
        Ensures an author field is present in the record.
        """
        return 'scientificNameAuthorship' in record_dict.keys()

    def _extract(self, body, record_dict):
        """
        Searches for the full author string, then breaks it up into smaller pieces
        (sections in brackets, individual names) if that's not found.

        :return: the start index of the author string if found, otherwise None
        """
        full_author = record_dict['scientificNameAuthorship']
        author_strings = [full_author] + [
            p.strip()
            for p in set(
                re.findall(r'\(([\w\s]+)\)', full_author)
                + re.findall(r'([\w.\s]+)', full_author)
            )
        ]
        for a in author_strings:
            matches = re.search(r'\s\(?{0}\)?(\s|$)'.format(re.escape(a)), body)
            return matches.start() if matches else None


class SimpleFieldParserStage(BaseParserStage):
    """
    A generic stage for searching for a certain field within the tag body (for the
    purposes of finding authors).
    """

    def __init__(self, field_name):
        self.field_name = field_name

    def _meets_criteria(self, body, record_dict):
        """
        Checks that the record contains a value for this field and that the value is
        present in the tag body.
        """
        return (
            self.field_name in record_dict.keys()
            and record_dict[self.field_name] in body
        )

    def _extract(self, body, record_dict):
        """
        If the value is at the end of the string, there is no point in continuing;
        otherwise, it looks for the first capitalised word after that value.

        :return: the start index of the estimated author string if found, else None.
        """
        field_value = record_dict[self.field_name]
        if re.search(f'{re.escape(field_value)}$', body):
            return len(body)
        split_by_value = re.split(f'{re.escape(field_value)}', body, 1)
        matches = re.search(r'\(?[A-Z]\w*', split_by_value[1])
        return (
            matches.start() + len(split_by_value[0]) + len(field_value)
            if matches
            else None
        )


class CapitalisedParserStage(BaseParserStage):
    '''
    The last resort stage in the search for authors - searches for the second capitalised word in
    the tag body.
    '''

    def _meets_criteria(self, body, record_dict):
        """
        Checks for multiple capitalised words in the tag body.
        """
        capit = re.findall(r'([A-Z]\S*)(?:\s|$)', body)
        return len(capit) > 1

    def _extract(self, body, record_dict):
        """
        Finds the start index of the second capitalised word.
        """
        matches = [m for m in re.finditer('[A-Z]', body)]
        return matches[1].start()
