from collections import OrderedDict

import re

from ckanext.nhm.lib.jinja_extensions import AuthorParserStage, SimpleFieldParserStage, CapitalisedParserStage


def extract_ranks(record):
    '''
    Extracts the values for each rank (if present) in the given record. Ranks missing from the record are not omitted.
    :param record: the record dict
    :return: the ranks as an OrderedDict in rank order.
    '''
    ranks = [
        ('kingdom', extract_kingdom),
        ('phylum', extract_phylum),
        ('class', extract_class),
        ('family', extract_family),
        ('genus', extract_genus),
        ('species', extract_species)
    ]
    # extract all the rank values
    extracted_ranks = [(rank, extractor(record)) for rank, extractor in ranks]
    # filter out the missing values and return as an OrderedDict
    return OrderedDict([(rank, value) for rank, value in extracted_ranks if value])


def extract_kingdom(record):
    '''
    Extract the kingdom value from the given record.
    :param record: the record dict
    :return: the kingdom value, or None if it is not present
    '''
    return record.get('kingdom', None)


def extract_phylum(record):
    '''
    Extract the phylum value from the given record.
    :param record: the record dict
    :return: the phylum value, or None if it is not present
    '''
    return record.get('phylum', None)


def extract_class(record):
    '''
    Extract the class value from the given record.
    :param record: the record dict
    :return: the class value, or None if it is not present
    '''
    return record.get('class', None)


def extract_family(record):
    '''
    Extract the family value from the given record.
    :param record: the record dict
    :return: the family value, or None if it is not present
    '''
    return record.get('family', None)


def extract_genus(record):
    '''
    Extract the genus value from the given record.
    :param record: the record dict
    :return: the genus value, or None if it is not present
    '''
    return record.get('genus', None)


def extract_species(record):
    '''
    Extract the species value from the given record. This is achieved by extracting the species from the
    `scientificName` field of the record (if there is one) and the removal of any extra details (such as the author)
    from this value.
    :param record: the record dict
    :return: the species value, or None if it is not present
    '''
    # first try extracting the species from the scientific name, which starts with the species but often has an author
    # or date after it
    scientific_name = record.get('scientificName', None)
    if scientific_name:
        # if it's just a single word, no need to parse
        first_space = re.search('\s', scientific_name)
        if not first_space:
            return scientific_name

        evaluators = OrderedDict()
        evaluators['authors'] = AuthorParserStage()
        evaluators['species'] = SimpleFieldParserStage('specificEpithet')
        evaluators['subgenus'] = SimpleFieldParserStage('subgenus')
        evaluators['capitalisation'] = CapitalisedParserStage()

        ix = None
        for t, e in evaluators.items():
            ix = e.evaluate(scientific_name, record)
            if ix:
                break

        if ix:
            return scientific_name[:ix].strip()

    return None
