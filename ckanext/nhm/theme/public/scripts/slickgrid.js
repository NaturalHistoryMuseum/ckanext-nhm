
// Slickgrid formatter for making the _id field into a link
var NHMFormatter = function(row, cell, value, columnDef, dataContext) {
  if(columnDef.id == "del"){
    return self.templates.deleterow
}

if(columnDef.id == "_id"){
    url = document.URL + '/record/' + value
    // Slickgrid uses preventDefault() preventing the link from working
    // So am using the onclick handler to change location
    return '<a target="_parent" href="' + url + '" onclick="window.top.location=this.href">View record</a>';
}

return value

};