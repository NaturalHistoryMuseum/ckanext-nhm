
// Get id of the view/* part of the URL
var pattern = /view\/[0-9a-z\-]+/;
var baseURL = document.URL.replace(pattern, '')

// Remove query string from BaseURL
if (baseURL.indexOf('?') > -1){
    baseURLparts = baseURL.split('?');
    baseURL = baseURLparts[0]
}

// Slickgrid formatter for making the _id field into a link
// and the dqi field into a traffic light!
var NHMFormatter = function(row, cell, value, columnDef, dataContext) {

    if(columnDef.id == "del"){
        return self.templates.deleterow
    }

    if(columnDef.id == "_id"){

        // Build URL, ensuring query is at the end
        var url = baseURL + 'record/' + value

        // Slickgrid uses preventDefault() preventing the link from working
        // So am using the onclick handler to change location
        return '<a title="View record" target="_parent" href="' + url + '" onclick="window.top.location=this.href">View</a>';
    }

    if(columnDef.id == 'dqi'){
      if (value == 'N/A' || value == 'Unknown'){
        return value;
      }
      var dqi_class = 'dqi_' + value.toLowerCase().replace(/[^a-z]/g, '');
      return '<div title="' + value + '" class="' + dqi_class + '"><span></span></div>';
    }

    return value

};




