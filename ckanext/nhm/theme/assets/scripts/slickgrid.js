// remove view/* part of the URL
let baseURL = document.URL.replace(/view\/[0-9a-z\-]+/, '');
let version = '';

// extract query string from baseURL
if (baseURL.indexOf('?') > -1) {
  let baseURLParts = baseURL.split('?');
  // remove the query string from our baseURL
  baseURL = baseURLParts[0];

  if (window.parent.ckan.views && window.parent.ckan.views.filters) {
    let versionFilter = window.parent.ckan.views.filters.get('__version__');
    if (typeof versionFilter !== 'undefined') {
      // version will be an array, get the first element as there should only ever be
      // one
      version = versionFilter[0];
    }
  }
}

if (version === '') {
  // if the version wasn't present, set it to null
  version = null;
} else {
  // otherwise convert the version to an integer
  version = Number.parseInt(version);
}

/**
 * Slickgrid formatter for:
 *  - making the id field into a link
 *  - dqi field into a traffic light
 *  - the associatedMedia field into a list of icons
 * @param row the row index
 * @param cell the column index
 * @param value the value of the cell
 * @param columnDef the column definition for this cell
 * @param dataContext the current dataContext (the entire row's data as an object)
 * @return {*} value to show in the cell, this can be raw html
 */
var NHMFormatter = function (row, cell, value, columnDef, dataContext) {
  if (columnDef.id === 'del') {
    return self.templates.deleterow;
  }

  if (columnDef.id === '_id') {
    // build URL, adding the record id to the end of the base url
    let url = baseURL + 'record/' + value;
    if (version != null) {
      url += '/' + version;
    }
    // Slickgrid uses preventDefault() preventing the link from working, so use the onclick
    // handler to change location
    return (
      '<a title="View record" target="_parent" href="' +
      url +
      '" onclick="window.top.location=this.href">View</a>'
    );
  }

  if (columnDef.id === 'gbifIssue') {
    var dqi_class;

    if (!dataContext['gbifID']) {
      dqi_class = 'unknown';
      value = 'Unknown';
    } else if (!value) {
      dqi_class = 'no-errors';
      value = 'No errors';
    } else {
      // Match and major errors
      var major_errors = [
        'TAXON_MATCH_NONE',
        'TYPE_STATUS_INVALID',
        'BASIS_OF_RECORD_INVALID',
      ];
      // Loop through all the major errors, and see if they exist in the value
      for (i = 0; i < major_errors.length; i++) {
        if (value.indexOf(major_errors[i]) !== -1) {
          dqi_class = 'major-errors';
          break;
        }
      }
      if (!dqi_class) {
        dqi_class = 'minor-errors';
      }
    }

    return (
      '<div title="' +
      value +
      '" class="dqi-traffic-light dqi-' +
      dqi_class +
      '"><span></span></div>'
    );
  }

  if (columnDef.id === 'associatedMedia') {
    // this is a hack to stop the associatedMedia column being sortable
    columnDef.sortable = false;
    if (value.length > 0) {
      // return an image icon and a count of how many images there are for this record
      return '<i class="fas fa-image"></i> x' + value.length;
    } else {
      // if there are no images, just return nothing
      return '';
    }
  }

  // if we don't want to override the functionality, just return the value for the field
  if (value && typeof value === 'string') {
    value = value.replace(/(https?:\/\/[^ ]+)/g, '<a href="$1">$1</a>');
  }
  return value;
};
