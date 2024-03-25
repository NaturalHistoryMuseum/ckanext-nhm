#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
import abc
from collections import namedtuple
from dataclasses import dataclass
from typing import List, Optional

import requests
from cachetools import cached, TTLCache

from ckanext.nhm.lib.taxonomy import extract_ranks

Link = namedtuple("Link", ("text", "url"))


@dataclass
class Site(abc.ABC):
    """
    An external site we can link to from a specimen record page.
    """

    name: str
    icon_url: str

    @abc.abstractmethod
    def get_links(self, record: dict) -> List[Link]:
        """
        Returns a list of Links from the passed record.

        :param record: the record dict
        """
        ...


@dataclass
class RankedTemplateSite(Site):
    """
    A site based on a templated URL filled in with the taxonomy ranks available in the
    record.
    """

    url_template: str

    def get_links(self, record: dict) -> List[Link]:
        ranks = extract_ranks(record)
        return [Link(rank, self.url_template.format(rank)) for rank in ranks.values()]


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def _get_gbif_record(occurrence_id: str, institution_code: str) -> Optional[dict]:
    """
    Given an occurrence ID and an institution code, returns the GBIF record for it, or
    None if exactly one GBIF record couldn't be found. This function is protected with a
    TTL cache to avoid hitting GBIF over and over again for the same occurrence ID
    query.

    :param occurrence_id: an occurrence ID
    :param institution_code: an institution code, this will probably be NHMUK really
    """
    if occurrence_id is None or institution_code is None:
        return None

    try:
        r = requests.get(
            "https://api.gbif.org/v1/occurrence/search",
            params={
                "occurrenceID": occurrence_id,
                "institutionCode": institution_code,
            },
            timeout=5
        )
    except requests.Timeout:
        return None

    if r.ok:
        results = r.json()
        if results.get("count") == 1:
            return results["results"][0]

    return None


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def _get_phenome10k_record(gbif_key: str) -> Optional[dict]:
    """
    Given a gbif key, returns the Phenome10k record for it, or None if exactly one
    Phenome10k record couldn't be found. This function is protected with a TTL cache to
    avoid hitting Phenome10k over and over again for the same gbif key query.

    :param gbif_key: the gbif key of the record
    """
    r = requests.get(
        "https://www.phenome10k.org/api/v1/scan/search",
        params={"gbif_occurrence_id": gbif_key},
    )
    if r.ok:
        results = r.json()
        if results["query_success"] and results["count"] == 1:
            return results["records"][0]

    return None


class Phenome10kSite(Site):
    """
    Site which uses the GBIF API and Phenome10k API to find associated 3D data on
    Phenome10k.
    """

    def get_links(self, record: dict) -> List[Link]:
        links = []
        try:
            gbif_record = _get_gbif_record(
                record.get("occurrenceID"), record.get("institutionCode", "NHMUK")
            )
            if gbif_record and "key" in gbif_record:
                p10k_record = _get_phenome10k_record(gbif_record["key"])
                if p10k_record:
                    links.append(
                        Link(p10k_record["scientific_name"], p10k_record["url"])
                    )
        except (requests.RequestException, KeyError):
            pass
        return links


class GBIFSite(Site):
    """
    Site that provides links to species and occurrence pages associated with the given
    record.
    """

    def get_links(self, record: dict) -> List[Link]:
        links = []

        try:
            gbif_record = _get_gbif_record(
                record.get("occurrenceID"), record.get("institutionCode", "NHMUK")
            )
            if gbif_record:
                links_parts = [
                    ("https://gbif.org/occurrence/{}", "catalogNumber", "key"),
                    (
                        "https://gbif.org/species/{}",
                        "scientificName",
                        "acceptedTaxonKey",
                    ),
                ]
                for url_template, name_key, url_key in links_parts:
                    if name_key in gbif_record and url_key in gbif_record:
                        links.append(
                            Link(
                                gbif_record[name_key],
                                url_template.format(gbif_record[url_key]),
                            )
                        )
        except requests.RequestException:
            pass

        return links


# Taxonomy searches
BHL = RankedTemplateSite(
    name="Biodiversity Heritage Library",
    icon_url="https://www.biodiversitylibrary.org/favicon.ico",
    url_template="https://www.biodiversitylibrary.org/name/{}",
)
CoL = RankedTemplateSite(
    name="Catalogue of Life",
    icon_url="https://www.catalogueoflife.org/images/col_square_logo.jpg",
    url_template="https://www.catalogueoflife.org/col/search/all/key/{}",
)
PBDB = RankedTemplateSite(
    name="Paleobiology Database",
    icon_url="https://paleobiodb.org/favicon.ico",
    url_template="https://paleobiodb.org/classic/checkTaxonInfo?taxon_name={}",
)
Mindat = RankedTemplateSite(
    name="Mindat",
    icon_url="https://www.mindat.org/favicon.ico",
    url_template="https://www.mindat.org/search.php?search={}",
)
GBIF = GBIFSite(
    name="GBIF",
    icon_url="https://gbif.org/favicon.ico",
)
P10K = Phenome10kSite(
    name="Phenome10k",
    icon_url="https://www.phenome10k.org/static/icons/favicon.ico",
)


def get_sites(record: dict) -> List[Site]:
    """
    Given a record, returns a list of sites that may be able to provide relevant links.

    :param record: a record dict
    """
    searches = {
        "BMNH(E)": [BHL, CoL, GBIF, P10K],
        "BOT": [BHL, CoL, GBIF, P10K],
        "MIN": [Mindat],
        "PAL": [PBDB, GBIF, P10K],
        "ZOO": [BHL, CoL, GBIF, P10K],
        # if there is no collection code, just check the BHL and CoL. This catches index
        # lot entries
        None: [BHL, CoL],
    }

    # if no collection code is available, default to None
    return searches.get(record.get("collectionCode", None), [])
