#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from collections import OrderedDict
from typing import Callable

import requests
from ckanext.nhm.lib.taxonomy import extract_ranks


class Site(object):
    def __init__(
        self,
        name,
        site_icon_url,
        link_template: str = None,
        link_callback: Callable[..., tuple] = None,
    ):
        self.name = name
        self.site_icon_url = site_icon_url
        if link_template:
            self.get_link = lambda x: link_template.format(x)
        elif link_callback:
            self.get_link = link_callback
        else:
            raise ValueError('Site requires either template or callback.')

    def rank_links(self, record):
        ranks = extract_ranks(record)
        if ranks:
            return OrderedDict.fromkeys(
                [(rank, self.get_link(rank)) for rank in ranks.values()]
            )
        else:
            return []


# Taxonomy searches
BHL = Site(
    name='Biodiversity Heritage Library',
    site_icon_url='https://www.biodiversitylibrary.org/favicon.ico',
    link_template='https://www.biodiversitylibrary.org/name/{}',
)
CoL = Site(
    name='Catalogue of Life',
    site_icon_url='https://www.catalogueoflife.org/images/col_square_logo.jpg',
    link_template='https://www.catalogueoflife.org/col/search/all/key/{}',
)
PBDB = Site(
    name='Paleobiology Database',
    site_icon_url='https://paleobiodb.org/favicon.ico',
    link_template='https://paleobiodb.org/classic/checkTaxonInfo?taxon_name={}',
)
Mindat = Site(
    name='Mindat',
    site_icon_url='https://www.mindat.org/favicon.ico',
    link_template='https://www.mindat.org/search.php?search={}',
)

SEARCHES = {
    'BMNH(E)': [BHL, CoL],
    'BOT': [BHL, CoL],
    'MIN': [Mindat],
    'PAL': [PBDB],
    'ZOO': [BHL, CoL],
    # if there is no collection code, just check the BHL and CoL. This catches index lot entries.
    None: [BHL, CoL],
}


def get_taxonomy_searches(record):
    """
    Given a record retuns the sites that are relevant to it.

    :param record: the record dict
    :return: a list of sites
    """
    # if no collection code is available, default to None
    relevant_searches = SEARCHES.get(record.get('collectionCode', None), [])
    return [(s.name, s.site_icon_url, s.rank_links(record)) for s in relevant_searches]


def _p10k_api(gbif_record):
    gbif_key = gbif_record.get('key')
    r = requests.get(
        'https://www.phenome10k.org/api/v1/scan/search',
        params={'gbif_occurrence_id': gbif_key},
    )
    if not r.ok:
        return False
    results = r.json()
    if results['query_success'] and results['count'] == 1:
        p10k_record = results['records'][0]
        return p10k_record.get('scientific_name'), p10k_record.get('url')
    return False


P10k = Site(
    name='Phenome10k',
    site_icon_url='https://www.phenome10k.org/static/icons/favicon.ico',
    link_callback=_p10k_api,
)


def _get_gbif_record(record):
    if 'occurrenceID' not in record:
        return False
    r = requests.get(
        'https://api.gbif.org/v1/occurrence/search',
        params={
            'occurrenceID': record.get('occurrenceID'),
            'institutionCode': record.get('institutionCode', 'NHMUK'),
        },
    )
    if r.ok:
        results = r.json()
        if results.get('count') == 1:
            return results['results'][0]
    return False


def get_gbif_links(record):
    gbif_record = _get_gbif_record(record)
    if not gbif_record:
        return []
    all_links = []
    gbif_links = [
        (
            gbif_record.get('catalogNumber'),
            f'https://gbif.org/occurrence/{gbif_record.get("key")}',
        )
    ]
    if 'acceptedTaxonKey' in gbif_record:
        gbif_links.append(
            (
                gbif_record.get('scientificName'),
                f'https://gbif.org/species/{gbif_record.get("acceptedTaxonKey")}',
            )
        )
    all_links.append(('GBIF', 'https://gbif.org/favicon.ico', gbif_links))
    p10k_link = P10k.get_link(gbif_record)
    if p10k_link:
        all_links.append((P10k.name, P10k.site_icon_url, [p10k_link]))
    return all_links
