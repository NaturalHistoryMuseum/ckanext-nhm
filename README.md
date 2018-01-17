ckanext-nhm
===========

[![Travis branch](https://img.shields.io/travis/NaturalHistoryMuseum/ckanext-nhm/master.svg?style=flat-square)](https://travis-ci.org/NaturalHistoryMuseum/ckanext-nhm) [![Coveralls github branch](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-nhm/master.svg?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-nhm)

CKAN extension for data.nhm.ac.uk

paster datastore update-stats -c /etc/ckan/default/development.ini



Caching
=======

#### NGINX

Datastore API searches are cached by the NGINX proxy.  

To clear the NGINX cache, issue a PURGE HTTP request:

Production: 

```bash
curl -X PURGE data.nhm.ac.uk
```

Staging: 

```bash
curl -X PURGE http://data-nlb-stg-1.nhm.ac.uk
```

#### Memcached

Memory intensive function calls are cached with memcached. 

```bash
echo 'flush_all' | nc localhost 11211
```

#### Clearing Cache

Caches are cleared on dataset updates see plugin.py:IPackageController


Requirements
============

Shapely<1.3 is added as a requirement but is not used by ckanext-nhm.

This is to fix a bug with ckanext-spatial trying to install an incompatible version.
 
See https://github.com/ckan/ckanext-spatial/issues/94.
