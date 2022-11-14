#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK


def generate_eml(package, resource):
    """
    Given a package and a resource, return some EML that can be used in a download of
    the resource. This XML string still has two placeholders in it: pub_date and
    date_stamp which are filled in by the ckanpackager.

    :param package: the package dict
    :param resource: the resource dict
    :return: the EML as a string
    """
    # use empty strings as defaults just in case some of these fields don't exist. They should, but
    # we don't want to raise an exception and therefore stop the request from being sent if
    # something is missing
    formatting_data = {
        'resource_id': resource['id'],
        'title': resource.get('name', ''),
        'abstract': resource.get('description', ''),
        'license': package.get('license_title', 'License not specified'),
        'package_name': package.get('name', ''),
        'additional_metadata': '',
    }

    # only include DOI data if we have some to provide
    if 'doi' in package:
        formatting_data[
            'additional_metadata'
        ] = '''
    <additionalMetadata>
      <metadata>
        <gbif>
          <dateStamp>{{date_stamp}}</dateStamp>
          <citation identifier="https://doi.org/{doi}">{citation}</citation>
          <resourceLogoUrl>http://data.nhm.ac.uk/images/logo.png</resourceLogoUrl>
        </gbif>
      </metadata>
    </additionalMetadata>
        '''.format(
            **{
                'doi': package['doi'],
                'citation': 'Natural History Museum http://data.nhm.ac.uk ({0}): {1}'.format(
                    package.get('doi_date_published', '')[:4], package.get('title', '')
                ),
            }
        ).strip()

    # build the xml string and return it
    return '''
<?xml version="1.0" encoding="UTF-8"?>
<eml:eml xmlns:eml="eml://ecoinformatics.org/eml-2.1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    packageId="{resource_id}" scope="system" system="http://gbif.org" xml:lang="en"
                    xsi:schemaLocation="eml://ecoinformatics.org/eml-2.1.1 http://rs.gbif.org/schema/eml-gbif-profile/1.0.2/eml.xsd">
  <dataset>
    <title>{title}</title>
    <creator>
      <organizationName>The Natural History Museum, London</organizationName>
      <electronicMailAddress>data@nhm.ac.uk</electronicMailAddress>
      <onlineUrl>http://data.nhm.ac.uk</onlineUrl>
    </creator>
    <metadataProvider>
      <organizationName>The Natural History Museum, London</organizationName>
      <electronicMailAddress>data@nhm.ac.uk</electronicMailAddress>
      <onlineUrl>http://data.nhm.ac.uk</onlineUrl>
    </metadataProvider>
    <pubDate>{{pub_date}}</pubDate>
    <language>en</language>
    <abstract>
      <para>{abstract}</para>
    </abstract>
    <keywordSet>
      <keyword>Occurrence</keyword>
      <keywordThesaurus>GBIF Dataset Type Vocabulary: http://rs.gbif.org/vocabulary/gbif/dataset_type.xml</keywordThesaurus>
    </keywordSet>
    <intellectualRights>
      <para>{license}</para>
    </intellectualRights>
    <distribution scope="document">
      <online>
        <url function="information">http://data.nhm.ac.uk/dataset/{package_name}</url>
      </online>
    </distribution>
    <contact>
      <organizationName>The Natural History Museum, London</organizationName>
      <electronicMailAddress>data@nhm.ac.uk</electronicMailAddress>
      <onlineUrl>http://data.nhm.ac.uk</onlineUrl>
    </contact>
  </dataset>
  {additional_metadata}
</eml:eml>
'''.format(
        **formatting_data
    ).strip()
