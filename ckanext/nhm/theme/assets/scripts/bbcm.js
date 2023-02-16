const baseUrl = window.location.origin;

// these are the species we're going to show on the map
const names = [
  'Pieris brassicae',
  'Pieris rapae',
  'Pieris napi',
  'Gonepteryx rhamni',
  'Melanargia galathea',
  'Lycaena phlaeas',
  'Pyronia tithonus',
  'Maniola jurtina',
  'Aphantopus hyperantus',
  'Pararge aegeria',
  'Polygonia c-album',
  'Vanessa cardui',
  'Aglais urticae',
  'Vanessa atalanta',
  'Aglais io',
  'Polyommatus icarus',
  'Celastrina argiolus',
  'Autographa gamma',
  'Zygaena filipendulae',
  'Euplagia quadripunctaria',
];

// these are the common names of the above species, note that the order is important
const commonNames = [
  'Large White',
  'Small White',
  'Green-veined White',
  'Brimstone',
  'Marbled White',
  'Small Copper',
  'Gatekeeper',
  'Meadow Brown',
  'Ringlet',
  'Speckled Wood',
  'Comma',
  'Painted Lady',
  'Small Tortoiseshell',
  'Red Admiral',
  'Peacock',
  'Common Blue',
  'Holly Blue',
  'Silver Y Moth',
  'Six spot Burnet Moth',
  'Jersey Tiger',
];

// add the names to the list in the details div
const namesContainer = document.getElementById('names');
for (let i = 0; i < names.length; i++) {
  const nameElement = document.createElement('li');
  nameElement.innerHTML = commonNames[i] + ' (<i>' + names[i] + '</i>)';
  namesContainer.appendChild(nameElement);
}

// create a map centred on gb
const map = L.map('map').setView([55.485079037526134, -3.2080078125000004], 6);

// add a base layer from osm
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// the version to search at
const version = new Date().getTime();

// the filters needed search for the species names at the right version
const filters = [
  {
    simple_query_string: {
      fields: ['data.scientificName.full'],
      query: '(' + names.join(') | (') + ')',
      default_operator: 'and',
    },
  },
  {
    term: {
      'meta.versions': version,
    },
  },
];

// the raw parameters needed for our tile fetches
const params = {
  style: 'plot',
  // boost the size a smidge (default is 4)
  point_radius: 6,
  indexes: 'nhm-05ff2255-c38a-40c9-b657-4ccb55ab2feb',
  search: JSON.stringify({
    query: {
      bool: {
        filter: filters,
      },
    },
  }),
};

// the tile and utf grid urls
const tile_url = baseUrl + '/tiles/{z}/{x}/{y}.png?';
const utf_grid_url = baseUrl + '/tiles/{z}/{x}/{y}.grid.json?';

// build the query string
let params_as_string = '';
Object.keys(params).forEach((key) => {
  params_as_string += key + '=' + encodeURIComponent(params[key]) + '&';
});
params_as_string = params_as_string.slice(0, -1);

// add the tile and utfgrid layers
L.tileLayer(tile_url + params_as_string).addTo(map);
const utfGridLayer = new L.UtfGrid(utf_grid_url + params_as_string, {
  resolution: 4,
  useJsonP: false,
});
utfGridLayer.addTo(map);

// on utf grid clicks, show a popup with specimen details
utfGridLayer.on('click', function (event) {
  // only show a popup if the click is on a point
  if (!!event.data) {
    const specs = [];
    if (event.data.count === 1) {
      // only one specimen here, no need to call the portal API, we already have the data
      const details = {
        name: event.data.data.scientificName,
        occurrenceID: event.data.data.occurrenceID,
      };
      // add a specimen image to the details if we can
      const mediaUrl = extractSpecimenImageUrl(event.data.data);
      if (!!mediaUrl) {
        details['media'] = mediaUrl;
      }
      specs.push(details);
      // pop it
      createPopup(event.latlng, specs);
    } else {
      // there are multiple points, query the portal API to get the details of each
      const points = [];
      event.data.geo_filter['coordinates'][0].forEach((pair) => {
        points.push({ lat: pair[1], lon: pair[0] });
      });
      fetch(baseUrl + '/api/3/action/datastore_search_raw', {
        method: 'post',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resource_id: '05ff2255-c38a-40c9-b657-4ccb55ab2feb',
          raw_result: true,
          search: {
            query: {
              bool: {
                // use the filters we used get the tiles, plus an additional geo
                // filter to only get the points in this area
                filter: filters.concat([
                  {
                    geo_polygon: {
                      'meta.geo': {
                        points: points,
                      },
                    },
                  },
                ]),
              },
            },
          },
        }),
      })
        .then(function (response) {
          return response.json();
        })
        .then(function (data) {
          // we got data, cycle through the hits and create a popup with the details of each
          // specimen
          data.result.hits.hits.forEach((hit) => {
            const details = {
              name: hit._source.data.scientificName,
              occurrenceID: hit._source.data.occurrenceID,
            };
            const mediaUrl = extractSpecimenImageUrl(hit._source.data);
            if (!!mediaUrl) {
              details['media'] = mediaUrl;
            }
            specs.push(details);
          });
          // pop it
          createPopup(event.latlng, specs);
        });
    }
  }
});

/**
 * Creates the a popup to show the specimen names and an image (if available).
 *
 * @param latlng the lat lon as an object
 * @param specs an array of specimen objects
 */
function createPopup(latlng, specs) {
  // build the popup (using strings, yuck but meh)
  let specimenPopupClasses = ['specimen_popup'];
  if (specs.length <= 3) {
    // if there 3 or fewer specimens at the location then we use this class too
    specimenPopupClasses.push('specimen_popup_small');
  }
  let popupContent = '<div class="' + specimenPopupClasses.join(' ') + '">';

  specs.forEach((specimen) => {
    popupContent += '<div class="specimen">';
    popupContent += '<div class="specimenDetails">';
    const commonName = mapToCommonName(specimen.name);
    if (!!commonName) {
      popupContent +=
        '<span class="commonName">' + commonName + '</span><br />';
    }
    popupContent +=
      '<span class="scientificName">' + specimen.name + '</span><br /><br />';
    popupContent +=
      '<a target="_blank" href="' +
      baseUrl +
      '/object/' +
      specimen.occurrenceID +
      '/' +
      version.toString() +
      '">View on the Data Portal</a>';
    popupContent += '</div>';

    if (!!specimen.media) {
      popupContent +=
        '<img class="specimenMedia" alt="Loading image..." src="' +
        specimen.media +
        '"/>';
    } else {
      popupContent +=
        '<span class="specimenMedia">No image available :(</span>';
    }
    popupContent += '</div>';
  });
  popupContent += '</div>';
  // fire it out
  L.popup({ minWidth: 500 })
    .setLatLng(latlng)
    .setContent(popupContent)
    .openOn(map);
}

/**
 * Map the given scientific name to its common name.
 *
 * @param name the scientific name
 * @returns {string|boolean} if mapped, the common name is returned, otherwise false is returned
 */
function mapToCommonName(name) {
  for (let i = 0; i < commonNames.length; i++) {
    // check to see if the scientific name provided matches any of our scientific names. Use a
    // prefix match to ensure we can still match when the authorship is appended to the name
    if (name.toLowerCase().startsWith(names[i].toLowerCase())) {
      return commonNames[i];
    }
  }
  return false;
}

/**
 * Extract the first specimen image we come across and return a URL to a thumbnail of it.
 *
 * @param specimen the specimen object
 * @returns {string|boolean} the URL or false if no specimen image was found
 */
function extractSpecimenImageUrl(specimen) {
  if (!!specimen.associatedMedia) {
    for (let i = 0; i < specimen.associatedMedia.length; i++) {
      const media = specimen.associatedMedia[i];
      if (media.category === 'Specimen' || media.category === 'specimen') {
        return `${media.identifier}/thumbnail`;
      }
    }
  }
  return false;
}
