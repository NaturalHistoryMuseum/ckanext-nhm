# Changelog

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

### Feature

- use nav slugs for the homepage search
- remove all references to ckanpackager

### Fix

- try once again to fix the overflowing text on resource list
- modify vds queries before and after converting
- allow for non-datastore resources in download button
- do not propogate errors from phenome10k api call
- set download button query from url

### Style

- data is plural

### Build System(s)

- update dependencies

### Chores/Misc

- pull in external link changes from #672

### Minor UI Changes

- replace record download link
- replace resource download link

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

### Fix

- do not propogate errors from phenome10k api call

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
- **deps**: bump node-forge and webpack-dev-server
- **deps**: bump json5 in /ckanext/nhm/theme/assets/scripts/apps/search
- **deps**: bump decode-uri-component
- **deps**: bump loader-utils

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
- add a button for resetting the download
- **search-app**: remove cached download when popup toggled
- **search-app**: add new dwc options and improve UI
- sort the show_extensions_versions by name
- add action which lists installed package extensions and their versions
- **search-app**: split popups into separate components, add new dl opts

### Fix

- use new download interface methods for replacing templates
- **accessibility**: add aria labels/alt text for all featured datasets
- **search-app**: actually trigger a download

### Refactor

- **search-app**: update node package versions

### Docs

- **citations**: add guidance on how to cite specimen collection images

### Tests

- go up one more dir to find src files
- remove references to old interface method
- add a test for the new show_extension_versions action

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

- **requirements**: use compatible release specifier for extensions

## v4.0.5 (2022-12-08)

### Fix

- fix patterns for package data

## v4.0.4 (2022-12-07)

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

- **requirements**: add ckanext-iiif as a dependency

## v4.0.1 (2022-11-29)

### Fix

- remove .decode() from object_rdf result
- change ckan.rdf.plugins to ckan.rdf.profiles

## v4.0.0 (2022-11-28)

### Fix

- **less**: add parentheses for less v4 compatibility
- update less and less-loader in beetle-iiif

### Docs

- add section delimiters and include-markdown

### Build System(s)

- **requirements**: update versions of ckan extensions
- set changelog generation to incremental
- pin minor versions of dependencies

### CI System(s)

- add cz_nhm dependency

### Chores/Misc

- use cz_nhm commitizen config

## v3.7.2 (2022-11-21)

### Breaking Changes

- install other extensions from PyPI. The current versions specified are not available so these will need to be changed before this is pushed to main.

### Feature

- add a new IIIF section on the record page
- expose a new helper which can build a record's IIIF manifest URL

### Fix

- ensure the geo_point radius is always passed as a number in queries

### Refactor

- switch all css to less

### Style

- apply formatting changes

### Build System(s)

- rebuild the search app after previous change (prod build)

### CI System(s)

- **commitizen**: fix message template

### Chores/Misc

- update dcat version
- improve commitizen message template
- fix license in package.json
- standardise package files

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

## v1.0.0-alpha (2019-07-23)

## v0.3.2 (2019-05-29)

## v0.3.1 (2019-05-01)

## v0.3.0 (2019-04-30)

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
