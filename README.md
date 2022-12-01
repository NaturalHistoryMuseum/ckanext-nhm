<!--header-start-->
<img src=".github/nhm-logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckanext-nhm

[![Tests](https://img.shields.io/github/workflow/status/NaturalHistoryMuseum/ckanext-nhm/Tests?style=flat-square)](https://github.com/NaturalHistoryMuseum/ckanext-nhm/actions/workflows/main.yml)
[![Coveralls](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-nhm/main?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-nhm)
[![CKAN](https://img.shields.io/badge/ckan-2.9.7-orange.svg?style=flat-square)](https://github.com/ckan/ckan)
[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg?style=flat-square)](https://www.python.org/)
[![Docs](https://img.shields.io/readthedocs/ckanext-nhm?style=flat-square)](https://ckanext-nhm.readthedocs.io)
[![Specimen records](https://img.shields.io/badge/dynamic/json.svg?color=brightgreen&label=specimens&query=%24.result.total&suffix=%20records&url=https%3A%2F%2Fdata.nhm.ac.uk%2Fapi%2F3%2Faction%2Fdatastore_search%3Fresource_id%3D05ff2255-c38a-40c9-b657-4ccb55ab2feb&style=flat-square)](https://data.nhm.ac.uk/dataset/collection-specimens/resource/05ff2255-c38a-40c9-b657-4ccb55ab2feb)

_A CKAN extension for the Natural History Museum's Data Portal._

<!--header-end-->

# Overview

<!--overview-start-->
This extension provides theming and specific functionality for the Natural History Museum's [Data Portal](https://data.nhm.ac.uk).

The codebase shows how to implement various plugins created by the Museum's developers; notably our new [ElasticSearch datastore](https://github.com/NaturalHistoryMuseum/ckanext-versioned-datastore) with versioned records.

<!--overview-end-->

# Installation

<!--installation-start-->
Path variables used below:
- `$INSTALL_FOLDER` (i.e. where CKAN is installed), e.g. `/usr/lib/ckan/default`
- `$CONFIG_FILE`, e.g. `/etc/ckan/default/development.ini`

1. Clone the repository into the `src` folder:

  ```bash
  cd $INSTALL_FOLDER/src
  git clone https://github.com/NaturalHistoryMuseum/ckanext-nhm.git
  ```

2. Activate the virtual env:

  ```bash
  . $INSTALL_FOLDER/bin/activate
  ```

3. Install the requirements from requirements.txt:

  ```bash
  cd $INSTALL_FOLDER/src/ckanext-nhm
  pip install -r requirements.txt
  ```

4. Run setup.py:

  ```bash
  cd $INSTALL_FOLDER/src/ckanext-nhm
  python setup.py develop
  ```

5. Add 'nhm' to the list of plugins in your `$CONFIG_FILE`:

  ```ini
  ckan.plugins = ... nhm
  ```

<!--overview-end-->

# Configuration

<!--installation-start-->
These are the options that can be specified in your .ini config file.
## **[REQUIRED]**

Name|Description|Options
--|--|--
`ckanext.nhm.specimen_resource_id`|ID for the specimens dataset|
`ckanext.nhm.indexlot_resource_id`|ID for the index lots dataset|
`ckanext.nhm.artefact_resource_id`|ID for the artefacts dataset|
`ckanext.nhm.abyssline_resource_id`|ID for the abyssline dataset|

<!--configuration-end-->

# Usage

<!--usage-start-->
## Actions

### `record_show`
Retrieve an individual record.

```python
from ckan.plugins import toolkit

data_dict = {
                'resource_id': RESOURCE_ID,
                'record_id': RECORD_ID,
                'version': OPTIONAL_RECORD_VERSION
            }

toolkit.get_action('record_show')(
    context,
    data_dict
)
```

### `object_rdf`
Get record RDF from its occurrence ID.

```python
from ckan.plugins import toolkit

data_dict = {
                'uuid': OCCURRENCE_ID,
                'version': OPTIONAL_RECORD_VERSION
            }

toolkit.get_action('object_rdf')(
    context,
    data_dict
)
```

## Commands

### `create-dataset-vocabulary`
Ensures the default dataset vocabulary and categories exists.

```bash
ckan -c $CONFIG_FILE nhm create-dataset-vocabulary
```

### `add-dataset-category`
Adds the given category to the dataset category vocabulary.

```bash
ckan -c $CONFIG_FILE nhm delete-dataset-category $NAME
```

### `delete-dataset-category`
Deletes the given dataset category from the vocabulary.

```bash
ckan -c $CONFIG_FILE nhm create-dataset-vocabulary $NAME
```

### `replace-resource-file`
Replaces the file associated with `$RESOURCE_ID` with `$PATH`, e.g. to replace a small dummy file
with a large one that was too big to upload initially.

```bash
ckan -c $CONFIG_FILE nhm replace-resource-file $RESOURCE_ID $PATH
```

<!--usage-end-->

# Testing

<!--testing-start-->
There is a Docker compose configuration available in this repository to make it easier to run tests.

To run the tests against ckan 2.9.x on Python3:

1. Build the required images
```bash
docker-compose build
```

2. Then run the tests.
   The root of the repository is mounted into the ckan container as a volume by the Docker compose
   configuration, so you should only need to rebuild the ckan image if you change the extension's
   dependencies.
```bash
docker-compose run ckan
```

The ckan image uses the Dockerfile in the `docker/` folder.

<!--testing-end-->
