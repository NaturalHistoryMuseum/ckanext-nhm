from collections import namedtuple


Site = namedtuple('Site', ['name', 'icon', 'link'])

BHL = Site(name='Biodiversity Heritage Library', icon='https://www.biodiversitylibrary.org/favicon.ico',
           link='https://www.biodiversitylibrary.org/name/{}')
CoL = Site(name='Catalogue of Life', icon='http://www.catalogueoflife.org/favicon.ico',
           link='http://www.catalogueoflife.org/col/search/all/key/{}')
PBDB = Site(name='Paleobiology Database', icon='https://paleobiodb.org/favicon.ico',
            link='https://paleobiodb.org/classic/checkTaxonInfo?taxon_name={}')
Mindat = Site(name='Mindat', icon='https://www.mindat.org/favicon.ico',
              link='https://www.mindat.org/search.php?search={}')


SITES = {
    'BMNH(E)': [BHL, CoL],
    'BOT': [BHL, CoL],
    'MIN': [Mindat],
    'PAL': [PBDB],
    'ZOO': [BHL, CoL],
    # if there is no collection code, just check the BHL and CoL. This catches index lot entries.
    None: [BHL, CoL]
}


def get_relevant_sites(record):
    '''
    Given a record retuns the sites that are relevant to it.
    :param record: the record dict
    :return: a list of sites
    '''
    # if no collection code is available, default to None
    return SITES.get(record.get('collectionCode', None), [])
