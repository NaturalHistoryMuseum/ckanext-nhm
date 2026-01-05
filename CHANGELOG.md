## v7.2.0 (2026-01-05)

### Feature

- set custom timeout for loading headers
- integrate vds updates

### Fix

- remove header warnings
- hide results until headers have loaded
- allow higher versions of elasticsearch-dsl

### Performance

- decrease sample probability to 0.05

### Build System(s)

- update vds dependency

## v7.1.4 (2025-12-29)

### Fix

- remove dev warning from prod build of search app

## v7.1.3 (2025-11-19)

### Fix

- show warnings if slug resolution fails
- add new disable_parsing flag to additional info blacklist

## v7.1.2 (2025-09-16)

### Minor UI Changes

- change some of the search placeholders

## v7.1.1 (2025-08-11)

### Docs

- briefly update download information
- add to API key statement
- clarify API docs links
- remove double spaces
- expand guidance on API limits

### Style

- wrap html

## v7.1.0 (2025-06-16)

### Feature

- display slug resolution warnings in multisearch ui
- add status indicator for collections dataset import

### Minor UI Changes

- add link to understanding and sharing the collection page

## v7.0.5 (2025-06-09)

### Fix

- add an id to hidden org field

### Docs

- docstring tidying
- replace return with returns in docstrings
- use variable logo, update tests badge

### Style

- remove space
- ruff formatting
- prettier formatting

### Build System(s)

- update ckantools

### CI System(s)

- set ruff target py version, add more ignores - avoid using fixes that don't work for python 3.8 (our current version) - ignore recommended ruff formatter conflicts - ignore more docstring rules
- remove pylint, add ruff lint rules Primarily the defaults plus pydocstyle and isort.
- update pre-commit repo versions
- add pull request validation workflow new workflow to check commit format and code style against pre-commit config
- update workflow files standardise format, change name of tests file

### Chores/Misc

- add pull request template
- update tool details in contributing guide

## v7.0.4 (2025-05-27)

### Fix

- add versions to queries

## v7.0.3 (2025-05-27)

### Minor UI Changes

- update aphid dataset text

## v7.0.2 (2025-05-07)

### Fix

- remove excel as a download option

## v7.0.1 (2025-05-06)

### Fix

- consider _inclusive fields true by default
- use unique resource ids from record list
- update vds endpoints

### Minor UI Changes

- change name, roles, and move people around

## v7.0.0 (2025-04-19)

### Breaking Changes

- update nhm plugin to work with vds vNext

### Feature

- update ckanext-versioned-datastore dep to dev head
- remove preps
- add artefact multisearch group management
- update field names to match new preparation mapping
- update nhm plugin to work with vds vNext

### Fix

- use r-strings for regexes with escape sequences
- allow collection resources to not exist when updating homepage stat counts
- remove case sensitive param
- fix missing line
- use the current hostname for slugs, not always data.nhm.ac.uk
- strip the specimen GUID to avoid including spaces
- add missing helper
- rebuild search app

### Refactor

- move field group management to the dataset views

### Docs

- add --rm to example test run docker compose cmd

### Tests

- fix the tests

### Build System(s)

- update iiif, query-dois, vds extensions
- remove unecessary version from docker compose def
- reference the vds preps branch not pypi version
- update mongo/elasticsearch
- update pyproject and pre-commit

### Minor UI Changes

- change the forced and ignored for index lots
- force specific groups for the sample dataset
- if the value on a record is a list, join it with a comma

## v6.9.8 (2025-01-16)

### Fix

- slightly increase the timeout for iiif status

## v6.9.7 (2025-01-15)

### Fix

- add js snippet to open slickgrid links in parent window

## v6.9.6 (2024-08-20)

### Fix

- taxa match type is string_contains
- add hasAssociatedMedia property to resource

### Style

- run prettier manually for other files
- run prettier manually for search
- run prettier manually for liv

## v6.9.5 (2024-08-02)

### Fix

- add nofollow to resource tags
- add nofollow to facet links

## v6.9.4 (2024-07-22)

### Fix

- only display warning if version is smaller than latest
- point legal link at legal page

## v6.9.3 (2024-07-15)

### Refactor

- move pages into dedicated legal section

## v6.9.2 (2024-07-15)

### Fix

- apparently maxsize was not unnecessary
- remove (probably) unnecessary maxsize of cache
- test if status.index route exists
- cache iiif status response for 300s
- reinsert + to URL creation
- remove GA code, don't need it anymore
- remove version from BBCM specimen links

### Refactor

- reduce size of ttl cache

## v6.9.1 (2024-07-08)

### Fix

- get mss status from source cache

## v6.9.0 (2024-07-08)

### Feature

- add link to help pages into footer
- add contact email for bii
- send enquiries to maintainer over collaborators or creator
- allow setting maintainer/contact email
- add link to status page in user icons, with indicator
- add integration with ckanext-status

### Fix

- change department label to "department or team"
- move temporal extent help message below the input
- get the reports list from status_list action
- catch error if status_list action doesn't exist
- change name of macro
- add status indicator when logged out as well
- change wording of specimen images help text
- use (un)available instead of (dis)connected

### Refactor

- remove api docs link, shorten some titles in footer

## v6.8.1 (2024-06-20)

### Fix

- add hidden org field when only one org available

## v6.8.0 (2024-06-10)

### Feature

- add help page for dataset permissions
- add org list to user profile

### Fix

- catch errors when parsing lat/lon for individual records
- only show org selector if more than one is available
- redirect /organisation to /organization
- remove new user invitation from org new member form
- allow non-sysadmin package editors to change org
- update search help page

### Style

- reformat search help header

## v6.7.1 (2024-05-14)

### Fix

- remove references to ckanext-twitter

## v6.7.0 (2024-05-07)

### Feature

- add LIV link for resources with image field
- change mirador link to LIV

### Fix

- allow passing liv mode and params as separate arguments
- remove "forgot password" button and replace with explanation

## v6.6.2 (2024-04-15)

### Fix

- create unique id for image associated with record

## v6.6.1 (2024-03-25)

### Fix

- use a smaller image for the goliath beetles
- disable rjsmin on liv script

## v6.6.0 (2024-03-25)

### Feature

- add link to liv from search ui image viewer
- add reset button
- add download button to overlay
- add no results message
- add clear filters button
- load filters from query
- initial commit for large image viewer (liv)
- add subtitle field to extras

### Fix

- only show no results message if search has been attempted
- reset state when setting query
- handle errors in multisearch request
- use query hash as abort signal, insert records and imgs together
- enable filters for index lots
- use string_contains for taxa search
- only show analytics when not debug
- define view components with shallowref
- make infinite scroll trigger earlier
- set minimum zoom level to allow further zooming out
- slow down repeated requests and disable auto load if many fail
- rate limit api calls from liv
- set limit param correctly
- add a timeout to GBIF API requests

### Refactor

- get all resources on app mount

### Chores/Misc

- update zoa
- remove extra multisearch
- remove unnecessary store import

### Minor UI Changes

- change viewer link and image on homepage
- add link to liv from beetle viewer

## v6.5.4 (2024-03-11)

### Fix

- remove random root init

## v6.5.3 (2024-02-26)

### Fix

- allow json-ld as an rdf format

## v6.5.2 (2024-02-13)

### Fix

- **search-ui**: rerun search even if image preset not added

## v6.5.1 (2024-02-05)

### Fix

- **search-ui**: return promise from loadAndCheckImages
- **search-ui**: update image filter when resources are changed
- **search-ui**: remove previous page's images when loading new set

### Refactor

- **search-ui**: rename birdwing preset

## v6.5.0 (2024-01-29)

### Feature

- add aohc page

## v6.4.2 (2024-01-22)

### Refactor

- remove mam patch and gallery overrides

## v6.4.1 (2024-01-15)

### Fix

- provide list of selected fields/headers to column picker

## v6.4.0 (2023-12-11)

### Feature

- use external class for links on new datacite page
- add a page about being a DataCite service provider

### Fix

- use /original endpoint for all iiif images, not just mss
- expand acronyms

## v6.3.0 (2023-12-11)

### Feature

- update 4th dataset (aphid slides)

### Fix

- check for aborted requests, sort images, move loading
- remove extra unnecessary image load in gallery component
- add key to parent div to prevent view rerendering

### Chores/Misc

- add build section to read the docs config

## v6.2.1 (2023-12-04)

### Fix

- use the correct version number for ckanext-doi
- use new test mode helper and update ckanext-doi

## v6.2.0 (2023-11-27)

### Feature

- add list/table view for record selection

### Fix

- check for the correct tab name
- remove scroll-snap from thumbnail select

### Refactor

- put records in the store, not in individual components
- move store into separate file
- simplify image selection from carousel

### Build System(s)

- fix build errors

### Minor UI Changes

- remove references to our twitter account
- add title to iiif viewer
- make the thumbnail carousel scroll vertically in a grid
- add beetle viewer page title and description

## v6.1.8 (2023-11-20)

### Fix

- include base/view-filters in all assets that require it to ensure ckan.views is available

## v6.1.7 (2023-11-13)

### Fix

- explicitly ignore field picker options
- add Google Analytics back into our analytics snippet

### Style

- reformat analytics snippet

## v6.1.6 (2023-10-30)

### Fix

- use the download_url property

## v6.1.5 (2023-10-16)

### Fix

- show root group when not 'and'
- exclude fields that have already been selected
- add a button to add currently selected field

### Minor UI Changes

- wrap the term editor up to lg screen size, hide label for name

## v6.1.4 (2023-10-05)

### Fix

- extract user id from tuple

## v6.1.3 (2023-10-05)

### Build System(s)

- change version specifiers for nhm ckan extensions

## v6.1.2 (2023-10-05)

### Fix

- remove additional nhm creator from generated eml

## v6.1.1 (2023-10-03)

### Fix

- update minor version of vds

### Chores/Misc

- add regex for version line in citation file
- add citation.cff to list of files with version
- add contributing guidelines
- add code of conduct
- add citation file
- update support.md links

## v6.1.0 (2023-09-25)

### Feature

- put some commonly useful DwC fields first in grid view

### Fix

- add other taxonomic ranks and prefer currentScientificName

## v6.0.4 (2023-09-18)

### Fix

- handle empty datastore resources

### Minor UI Changes

- edit site credits

## v6.0.3 (2023-08-21)

### Fix

- replace google analytics with adobe analytics
- load images on create gallery
- reload images on new search when view is gallery
- delay gallery tile resizing
- fix promise chaining on runSearch, lock image loading
- tile the gallery with js again
- make runSearch cancellable

### Refactor

- remove google analytics config

## v6.0.2 (2023-07-20)

### Fix

- add arg to js void calls
- change blank links to js void instead of hash
- validate download form before submitting

### Minor UI Changes

- reduce margin on bottom of header
- fiddle with header layout
- improve layout of footer
- set arial as the fallback font

## v6.0.1 (2023-07-18)

### Fix

- put the account icons on top

## v6.0.0 (2023-07-18)

### Fix

- try once again to fix the overflowing text on resource list

### Build System(s)

- update dependencies

## v5.8.2 (2023-07-17)

### Fix

- use hidden instead of clip so it works on ios
- truncate long resource names better
- improve spacing on header
- truncate very long resource names

## v5.8.1 (2023-07-17)

### Fix

- fix some display issues on mobile

## v5.8.0 (2023-07-17)

### Feature

- update fonts

### Docs

- update logos

### Minor UI Changes

- disable contextual alternates everywhere
- update logos

## v5.7.0 (2023-07-03)

### Feature

- add defensive code to ensure external sites don't prevent record pages loading

### Fix

- **search-app**: add default promises
- remove debug code
- **search-app**: add promises as status indicators for api requests
- update botany contact email
- prevent sending Nones to GBIF when looking up external site links

### Refactor

- move the code that retrieves a record from phenome10k into its own function to aid testing and caching
- reorganise the external links module into to have a more formal interface

### Style

- reformat imports
- reorganise imports
- remove unecessary object base class in Site def

### Tests

- add tests for gbif site
- add tests for p10k site and fix bugs found by adding tests
- add some basic external links tests

### Chores/Misc

- remove more debug code
- default the institutionCode to NHMUK

## v5.6.4 (2023-06-16)

### Feature

- use nav slugs for the homepage search
- remove all references to ckanpackager

### Fix

- do not propogate errors from phenome10k api call
- modify vds queries before and after converting
- allow for non-datastore resources in download button
- do not propogate errors from phenome10k api call
- set download button query from url

### Style

- data is plural

### Chores/Misc

- pull in external link changes from #672

### Minor UI Changes

- replace record download link
- replace resource download link

## v5.6.3 (2023-05-09)

### Fix

- use Mirador as an external IIIF viewer rather than UV

## v5.6.2 (2023-04-24)

### Fix

- add all loadable images to the previewer at the same time

## v5.6.1 (2023-04-11)

### Build System(s)

- update ckanext-contact version

## v5.6.0 (2023-04-11)

### Feature

- adds a subject line to the contact form

### Build System(s)

- fix postgres not loading when running tests in docker

### Chores/Misc

- remove "needs" from sync action
- move branch sync into its own file

### Minor UI Changes

- add date fields to default columns

## v5.5.1 (2023-04-04)

### Chores/Misc

- add branch sync workflow
- **contact form**: remove EEES option and redirect ES FIP

## v5.5.0 (2023-03-29)

### Feature

- send dataset contact emails to admin collaborators

### Fix

- replace masonry with 4 lines of css
- use Image instead of axios to check src, push to state when done

### Refactor

- move the mail logic out into its own module

### Build System(s)

- uninstall masonry

### Chores/Misc

- move comment to correct line
- remove unused variable in mail_alter hook

## v5.4.0 (2023-03-27)

### Feature

- add help popup for unloaded imgs

### Fix

- change user_show request method to post
- detect whether images are broken
- display something sensible in image alt text

## v5.3.0 (2023-03-20)

### Feature

- add notice on non-current record pages

### Build System(s)

- **deps**: update vds

### Minor UI Changes

- add an alert-info class and some spacing utils

## v5.2.2 (2023-03-06)

### Fix

- exclude unnecessary columns from search results

### Refactor

- change default fields for specimens/index lots

### Chores/Misc

- **contact form**: update email address for LS insects

## v5.2.1 (2023-02-20)

### Fix

- add empty content for group

## v5.2.0 (2023-02-20)

### Feature

- **search-ui**: feat: enable adding multiple/nested filters in a preset

### Docs

- fix api docs generation script

### Style

- apply prettier to js/vue/less
- fix line endings

### CI System(s)

- add prettier to pre-commit, exclude vendor/dist folders

### Chores/Misc

- small fixes to align with other extensions

## v5.1.1 (2023-02-13)

### Chores/Misc

- remove an exclamation mark from the record IIIF info

## v5.1.0 (2023-02-06)

### Feature

- allow multiple emails in the download UI

### Build System(s)

- bump vds version
- rebuild search app after merging dependabot updates
- **deps**: bump loader-utils
- **deps**: bump decode-uri-component
- **deps**: bump node-forge and webpack-dev-server
- **deps**: bump json5 in /ckanext/nhm/theme/assets/scripts/apps/search

### Minor UI Changes

- **search**: add links to tdwg and gbif for dwc

## v5.0.3 (2023-01-31)

### Docs

- **readme**: change blob url to raw

## v5.0.2 (2023-01-31)

### Docs

- **readme**: direct link to logo in readme
- **readme**: add specimens count badge back
- **readme**: fix github actions badge

## v5.0.1 (2023-01-31)

### Build System(s)

- bump query-dois version

## v5.0.0 (2023-01-30)

### Feature

- change featured dataset 4 to jtd
- sort the show_extensions_versions by name
- add action which lists installed package extensions and their versions
- add a button for resetting the download
- **search-app**: remove cached download when popup toggled
- **search-app**: add new dwc options and improve UI

### Fix

- **accessibility**: add aria labels/alt text for all featured datasets
- use new download interface methods for replacing templates
- **search-app**: actually trigger a download

### Refactor

- **search-app**: update node package versions

### Docs

- **citations**: add guidance on how to cite specimen collection images

### Tests

- go up one more dir to find src files
- add a test for the new show_extension_versions action
- remove references to old interface method

### Build System(s)

- **docker**: use 'latest' tag for test docker image

### Chores/Misc

- bump dependency versions
- **contact form**: update email addresses for LS insects and ES verts
- move tests into unit subdir
- reorganise the imports
- merge in new changes from dev

## v4.1.1 (2022-12-14)

### Build System(s)

- update minor versions of query-dois and vds

## v4.1.0 (2022-12-12)

### Feature

- **records.html**: adds a reverse total record sort to the records stats page

### Refactor

- move package.json into theme, remove less

### Docs

- **readme**: add instruction to install lessc globally

### Tests

- **Dockerfile**: fixes the Dockerfile for testing by installing ckanext-dcat

### Build System(s)

- **commitizen**: fix package.json path
- **requirements**: use compatible release specifier for extensions

## v4.0.5 (2022-12-08)

### Fix

- fix patterns for package data

## v4.0.4 (2022-12-07)

### Feature

- **search-app**: split popups into separate components, add new dl opts

### Fix

- use package data instead of relative paths

## v4.0.3 (2022-12-01)

## v4.0.2 (2022-12-01)

### Fix

- re-fix IIIF builder args issue
- add context and builder_args to build_iiif_identifier call
- **dcat**: change Format to format
- add view filters js to resource view snippet

### Refactor

- **featured**: change featured dataset 4 to predicts

### Docs

- **readme**: format test section
- **readme**: update installation steps
- **readme**: update ckan patch version in header badge

### Style

- replace %s style strings with f-strings
- remove u-strings
- **quotes**: use single quotes

### Build System(s)

- remove ckanext-dcat from dependencies entirely
- put dcat dependency link in setup.py
- fix version number
- **requirements**: add ckanext-iiif as a dependency

## v4.0.1 (2022-11-29)

### Fix

- remove .decode() from object_rdf result
- change ckan.rdf.plugins to ckan.rdf.profiles

## v4.0.0 (2022-11-28)

### Breaking Changes

- install other extensions from PyPI. The current versions specified are not available so these will need to be changed before this is pushed to main.

### Feature

- add a new IIIF section on the record page
- expose a new helper which can build a record's IIIF manifest URL

### Fix

- **less**: add parentheses for less v4 compatibility
- update less and less-loader in beetle-iiif

### Refactor

- switch all css to less

### Docs

- add section delimiters and include-markdown

### Style

- apply formatting changes

### Build System(s)

- **requirements**: update versions of ckan extensions
- set changelog generation to incremental
- pin minor versions of dependencies

### CI System(s)

- add cz_nhm dependency
- **commitizen**: fix message template

### Chores/Misc

- use cz_nhm commitizen config
- update dcat version
- improve commitizen message template
- fix license in package.json
- standardise package files

## v3.7.2 (2022-11-21)

### Fix

- ensure the geo_point radius is always passed as a number in queries

### Build System(s)

- rebuild the search app after previous change (prod build)

## v3.7.1 (2022-10-24)

## v3.7.0 (2022-10-17)

## v3.6.1.1 (2022-10-10)

## v3.6.1 (2022-10-10)

## v3.6.0 (2022-10-03)

## v3.5.0 (2022-09-20)

## v3.4.1 (2022-09-06)

## v3.4.0 (2022-08-30)

## v3.3.7 (2022-08-22)

## v3.3.6 (2022-08-15)

## v3.3.5 (2022-08-08)

## v3.3.4 (2022-07-11)

## v3.3.3 (2022-06-20)

## v3.3.2 (2022-06-13)

## v3.3.1 (2022-06-06)

## v3.3.0 (2022-05-30)

## v3.2.1 (2022-05-23)

## v3.2.0 (2022-05-23)

## v3.1.2 (2022-05-17)

## v3.1.1 (2022-05-03)

## v3.1.0 (2022-04-25)

## v3.0.30 (2022-04-04)

## v3.0.29 (2022-04-04)

## v3.0.28 (2022-03-28)

## v3.0.27 (2022-03-21)

## v3.0.26 (2022-03-21)

## v3.0.25 (2022-03-14)

## v3.0.24 (2022-03-07)

## v3.0.23 (2022-03-07)

## v3.0.22 (2022-02-28)

## v3.0.21 (2022-02-28)

## v3.0.20 (2022-02-21)

## v3.0.19 (2022-01-10)

## v3.0.18.1 (2021-11-22)

## v3.0.18 (2021-11-19)

## v3.0.17 (2021-11-18)

## v3.0.16 (2021-11-11)

## v3.0.15 (2021-11-11)

## v3.0.14 (2021-11-05)

## v3.0.13 (2021-11-05)

## v3.0.12 (2021-10-19)

## v3.0.11 (2021-10-12)

## v3.0.10 (2021-07-19)

## v3.0.9 (2021-07-07)

## v3.0.8 (2021-05-24)

## v3.0.7 (2021-05-19)

## v3.0.6 (2021-04-01)

## v3.0.5 (2021-03-11)

## v3.0.4 (2021-03-10)

## v3.0.3 (2021-03-09)

## v3.0.2 (2021-03-09)

## v3.0.1 (2021-03-09)

## v3.0.0 (2021-03-09)

## v0.3.7 (2019-10-31)

## v0.3.6 (2019-10-18)

## v0.3.5 (2019-10-11)

## v0.3.4 (2019-08-12)

## v0.3.3 (2019-08-07)

## v0.3.2 (2019-05-29)

## v0.3.1 (2019-05-01)

## v0.3.0 (2019-04-30)

## v1.0.0-alpha (2019-07-23)

## v0.2.10 (2018-12-07)

## v0.2.9 (2018-09-11)

## v0.2.8 (2018-09-07)

## v0.2.7 (2018-08-23)

## v0.2.6 (2018-07-24)

## v0.2.5 (2018-07-09)

## v0.2.4 (2018-07-09)

## v0.2.3 (2018-06-19)

## v0.2.2 (2018-06-14)

## v0.2.1 (2018-05-18)

## v0.2.0 (2018-02-06)

## v0.1.0 (2018-01-09)

## v0.0.1 (2017-12-07)
