#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from dataclasses import dataclass
from typing import Optional, List

import ckan.model as model
from cachetools import cached, TTLCache
from ckan.lib.helpers import url_for
from ckan.model.license import DefaultLicense
from ckan.plugins import toolkit
from ckanext.nhm.dcat.utils import rdf_resources
from ckanext.nhm.lib.helpers import get_specimen_resource_id, is_collection_resource_id
from contextlib import suppress
from functools import partial


def get_record_by_uuid(uuid, version=None) -> Optional['Record']:
    """
    Loop through all resources, and try and find the record.

    Currently this only works for specimens (as rdf_resources() only returns the
    specimens resource).
    """
    context = {'user': toolkit.c.user or toolkit.c.author}
    for resource_id in rdf_resources():
        with suppress(Exception):
            # search for the record
            search_data_dict = {
                'resource_id': resource_id,
                'filters': {
                    'occurrenceID': uuid,
                },
                'version': version,
            }
            # retrieve datastore record
            search_result = toolkit.get_action('datastore_search')(
                context, search_data_dict
            )
            records = search_result['records']
            if records:
                data = records[0]
                return Record(data['_id'], version, data, resource_id, context=context)
    return None


# cache for 5 mins
@cached(cache=TTLCache(maxsize=4096, ttl=300))
def get_specimen_by_uuid(
    uuid: str, version: Optional[int] = None
) -> Optional['Record']:
    with suppress(Exception):
        search_data_dict = {
            'resource_id': get_specimen_resource_id(),
            'filters': {
                'occurrenceID': uuid,
            },
            'version': version,
        }
        search_result = toolkit.get_action('datastore_search')({}, search_data_dict)
        records = search_result['records']
        if records:
            data = records[0]
            return Record(data['_id'], version, data, get_specimen_resource_id())
    return None


# define some custom fields that are set on the resource
TITLE_FIELD = '_title_field'
SUBTITLE_FIELD = '_subtitle_field'
IMAGE_FIELD = '_image_field'
IMAGE_DELIMETER_FIELD = '_image_delimiter'
IMAGE_LICENCE_FIELD = '_image_licence'
LATITUDE_FIELD = '_latitude_field'
LONGITUDE_FIELD = '_longitude_field'
# define a couple of DwC terms we'll use as defaults where appropriate
DWC_ASSOCIATED_MEDIA = 'associatedMedia'
DWC_LATITUDE = 'decimalLatitude'
DWC_LONGITUDE = 'decimalLongitude'
# define some image copyright defaults
DEFAULT_RIGHTS = '&copy; The Trustees of the Natural History Museum, London'
DEFAULT_IMAGE_LICENSE_ID = 'cc-by'


@dataclass
class RecordImage:
    """
    Simple class representing an image associated with a record.
    """

    url: str
    title: str
    license_title: str
    license_url: str
    rights: str = DEFAULT_RIGHTS
    record: Optional['Record'] = None
    is_mss_image: bool = False

    @property
    def is_iiif_image(self) -> bool:
        return self.is_mss_image or self.url.startswith(
            toolkit.config.get('ckanext.iiif.image_server_url')
        )

    @property
    def download_url(self) -> str:
        return f'{self.url}/original' if self.is_iiif_image else self.url

    @property
    def preview_url(self) -> str:
        return f'{self.url}/preview' if self.is_iiif_image else self.url

    @property
    def thumbnail_url(self) -> str:
        return f'{self.url}/thumbnail' if self.is_iiif_image else self.url


class Record:
    """
    A model class for a record.

    This class allows access to various information related to the record using the
    resource and package and will lazily load those entities as required.
    """

    def __init__(
        self,
        record_id: int,
        version: Optional[int] = None,
        data: Optional[dict] = None,
        resource_id: Optional[str] = None,
        package_id: Optional[str] = None,
        package_name: Optional[str] = None,
        package_id_or_name: Optional[str] = None,
        resource: Optional[dict] = None,
        package: Optional[dict] = None,
        context: Optional[dict] = None,
    ):
        """
        The only required init parameter is the record_id, however, most of the related
        information requires other parameters to be passed to make it possible to look
        them up. For example, just a record_id will not allow access to the record's
        data, a resource_id is required too.

        :param record_id: the record ID as an int
        :param version: the record's version
        :param data: the record's data
        :param resource_id: the resource ID this record comes from
        :param package_id: the package ID this record comes from
        :param package_name: the package name this record comes from
        :param package_id_or_name: the package ID or name. These are often used interchangeably in
                                   the CKAN action API so if you don't know which package identifier
                                   you have, use this.
        :param resource: the resource this record is from as a dict
        :param package: the package this record is from as a dict
        :param context: a context to use for any action API calls
        """
        self.id = record_id
        self.version = version
        self._data = data
        self._resource_id = resource_id
        self._resource = resource
        self._package_id = package_id
        self._package_name = package_name
        self._package_id_or_name = package_id_or_name
        self._package = package
        self._image_license = None
        self._images = None
        self._geojson = None
        self._context = (
            context
            if context
            else {
                'user': toolkit.c.user or toolkit.c.author,
                'auth_user_obj': toolkit.c.userobj,
            }
        )

    @property
    def data(self) -> dict:
        if not self._data:
            data_dict = dict(record_id=self.id, resource_id=self.resource_id)
            if self.version is not None:
                data_dict['version'] = self.version
            self._data = toolkit.get_action('record_show')(self._context, data_dict)[
                'data'
            ]
        return self._data

    @property
    def resource_id(self) -> str:
        if not self._resource_id:
            raise Exception('Resource ID not set')
        return self._resource_id

    @property
    def resource(self) -> dict:
        if not self._resource:
            self._set_resource()
        return self._resource

    def _set_resource(self):
        """
        Sets up the resource data.
        """
        data_dict = dict(id=self.resource_id)
        self._resource = toolkit.get_action('resource_show')(self._context, data_dict)

    def _set_package(self):
        """
        Sets up the package dict using the package ID or name depending on which one is
        available.

        If neither are available, this function will attempt to get the package ID from
        the resource model object. If none of these strategies work, an Exception is
        thrown.
        """
        id_or_name = (
            self._package_id or self._package_name or self._package_id_or_name or None
        )
        # if we don't have an id or a name for the package, see if we can use the resource
        if not id_or_name and self._resource_id:
            resource = model.Resource.get(self.resource_id)
            if resource:
                id_or_name = resource.get_package_id()
        if not id_or_name:
            raise Exception('Package id or name not available')
        self._package = toolkit.get_action('package_show')(
            self._context, dict(id=id_or_name)
        )
        self._package_id = self._package['id']
        self._package_name = self._package['name']
        # set this to None to avoid confusion
        self._package_id_or_name = None

    @property
    def package_id(self) -> str:
        if not self._package_id:
            self._set_package()
        return self._package_id

    @property
    def package_name(self) -> str:
        if not self._package_name:
            self._set_package()
        return self._package_name

    @property
    def package(self) -> dict:
        if not self._package:
            self._set_package()
        return self._package

    @property
    def title(self) -> str:
        # this assumes that None is not a key in self.data but that's reasonable tbh
        return self.data.get(self.resource.get(TITLE_FIELD), f'Record {self.id}')

    def url(self, use_package_id=False) -> str:
        """
        Returns the URL for this record. If the version is present it is included in the
        URL.

        :param use_package_id: whether to use the package ID in the URL or the package name, the
                               default is the package name (i.e. use_package_id=False)
        :return: the record URL
        """
        name_or_id = self.package_id if use_package_id else self.package_name
        create_url = partial(
            url_for,
            'record.view',
            package_name=name_or_id,
            resource_id=self.resource_id,
            record_id=self.id,
        )
        if self.version is not None:
            return create_url(version=self.version)
        else:
            return create_url()

    @property
    def image_license(self) -> DefaultLicense:
        """
        Retrieves the default image license for the record based on the image licence
        field set on the resource.

        :return: the licence model object
        """
        if not self._image_license:
            license_registry = model.Package.get_license_register()
            id_options = []
            chosen_license = self.resource.get(IMAGE_LICENCE_FIELD)
            if chosen_license:
                # add the shortened form too in case we get a hit on that
                id_options.extend([chosen_license, chosen_license[:5].lower()])
            for license_id in id_options:
                if license_id in license_registry:
                    self._image_license = license_registry[license_id]
                    break
            else:
                self._image_license = license_registry[DEFAULT_IMAGE_LICENSE_ID]
        return self._image_license

    @property
    def image_field(self) -> Optional[str]:
        """
        Returns the name of the field in the record that contains the image data. If no
        field is specified at the resource level then we check for a DwC
        associated_media field and use it if we find it. If no field name can be
        resolved, return None.

        :return: the name of the field in the record containing the image data or None if there
                 isn't one
        """
        return self.resource.get(
            IMAGE_FIELD, DWC_ASSOCIATED_MEDIA if self.is_dwc else None
        )

    @property
    def images(self) -> List[RecordImage]:
        """
        Retrieves a list of RecordImages associated with this record.

        :return: a list of RecordImage objects
        """
        if self._images is None:
            self._images = []
            # TODO: there used to be a check that this wasn't _id here, do we really need that?
            if self.image_field is not None:
                raw_images = self.data.get(self.image_field)
                if raw_images:
                    is_mss_image = is_collection_resource_id(self._resource_id)
                    if isinstance(raw_images, str):
                        # if we have a delimiter, use it to split the images
                        delimiter = self.resource.get(IMAGE_DELIMETER_FIELD)
                        images = (
                            raw_images.split(delimiter) if delimiter else [raw_images]
                        )
                        for image in filter(None, (image.strip() for image in images)):
                            self._images.append(
                                RecordImage(
                                    image,
                                    self.title,
                                    self.image_license.title,
                                    self.image_license.url,
                                    DEFAULT_RIGHTS,
                                    self,
                                    is_mss_image,
                                )
                            )
                    elif isinstance(raw_images, list):
                        for image in raw_images:
                            image_url = image.get('identifier')
                            if image_url:
                                license_title = image.get(
                                    'license', self.image_license.title
                                )
                                licence_url = image.get(
                                    'license', self.image_license.url
                                )
                                rights = image.get('rightsHolder', DEFAULT_RIGHTS)
                                self._images.append(
                                    RecordImage(
                                        image_url,
                                        image.get('title', self.title),
                                        license_title,
                                        licence_url,
                                        rights,
                                        self,
                                        is_mss_image,
                                    )
                                )
        return self._images

    @property
    def is_dwc(self):
        return self.resource['format'].lower() == 'dwc'

    @property
    def geojson(self) -> Optional[dict]:
        """
        If latitude and longitude fields are set on the resource, or can be inferred,
        extract the values from the record data and return a GeoJSON compatible Point
        where the record is located.

        :return: None if the latitude and longitude couldn't be identified or a GeoJSON Point
        """
        lat_field = self.resource.get(
            LATITUDE_FIELD, DWC_LATITUDE if self.is_dwc else None
        )
        lon_field = self.resource.get(
            LONGITUDE_FIELD, DWC_LONGITUDE if self.is_dwc else None
        )

        if not lat_field or not lon_field:
            return None

        try:
            latitude = float(self.data.get(lat_field))
            longitude = float(self.data.get(lon_field))
        except (ValueError, TypeError):
            return None

        # create a piece of GeoJSON to point at the specific record location on a map
        # (note the longitude then latitude ordering required by GeoJSON)
        return dict(type="Point", coordinates=[longitude, latitude])
