from collections import namedtuple


Site = namedtuple(u'Site', [u'name', u'icon', u'link'])

BHL = Site(name=u'Biodiversity Heritage Library', icon=u'https://www.biodiversitylibrary.org/favicon.ico',
           link=u'https://www.biodiversitylibrary.org/name/{}')
CoL = Site(name=u'Catalogue of Life', icon=u'https://www.catalogueoflife.org/sites/default/files/favicon.gif',
           link=u'http://www.catalogueoflife.org/col/search/all/key/{}')
PBDB = Site(name=u'Paleobiology Database', icon=u'https://paleobiodb.org/favicon.ico',
            link=u'https://paleobiodb.org/classic/checkTaxonInfo?taxon_name={}')
Mindat = Site(name=u'Mindat', icon=u'https://www.mindat.org/favicon.ico',
              link=u'https://www.mindat.org/search.php?search={}')


SITES = {
    u'BMNH(E)': [BHL, CoL],
    u'BOT': [BHL, CoL],
    u'MIN': [Mindat],
    u'PAL': [PBDB],
    u'ZOO': [BHL, CoL],
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
    return SITES.get(record.get(u'collectionCode', None), [])
