ckanext-nhm
===========

CKAN extension for data.nhm.ac.uk

paster datastore update-stats -c /etc/ckan/default/development.ini

echo 'flush_all' | nc localhost 11211


Requirements
============

Shapely<1.3 is added as a requirement but is not used by ckanext-nhm.

This is to fix a bug with ckanext-spatial trying to install an incompatible version.
 
See https://github.com/ckan/ckanext-spatial/issues/94.
