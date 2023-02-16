ckan.module('expand-authors', function ($, _) {
  var self, abbrAuthors, allAuthors, isAbbr;
  return {
    initialize: function () {
      /* Initialises the module.
       */
      self = this;
      var abbr = self.el.children('abbr');
      allAuthors = abbr.attr('title');
      abbrAuthors = self.el.html();
      isAbbr = true;
      self.el.on('click', jQuery.proxy(this._onClick, this));
    },

    _onClick: function (event) {
      event.preventDefault();
      self.el.html(isAbbr ? allAuthors : abbrAuthors);
      isAbbr = !isAbbr;
    },
  };
});
