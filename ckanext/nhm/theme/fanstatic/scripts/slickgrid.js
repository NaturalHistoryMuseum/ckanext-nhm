
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

    if(columnDef.id == 'gbifIssue'){
      var dqi_class;

        if(dataContext['gbifID'] === null){
            dqi_class = 'unknown'
            value = 'Unknown'
        }else if(value === null){
            dqi_class = 'no-errors'
            value = 'No errors'
        }else{
        // Match and major errors

        var major_errors = ['TAXON_MATCH_NONE', 'TYPE_STATUS_INVALID', 'BASIS_OF_RECORD_INVALID']
        // Loop through all the major errors, and see if they exist in the value
        for(i=0;i<major_errors.length;i++){
          if(value.indexOf(major_errors[i])!==-1){
              dqi_class = 'major-errors'
              break
          }
        }
        if(!dqi_class){
          dqi_class = 'minor-errors'
        }
        }

      return '<div title="' + value + '" class="dqi-traffic-light dqi-' + dqi_class + '"><span></span></div>';
    }

    return value

};




