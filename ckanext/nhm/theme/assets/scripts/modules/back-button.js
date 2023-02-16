/* Table toggle more
 * When a table has more things to it that need to be hidden and then shown more
 */
this.ckan.module('back-button', function ($, _) {
  var pattern = /view\/([0-9a-z\-]+)/;

  return {
    /* Initialises the module setting up elements and event listeners.
     *
     * Returns nothing.
     */
    initialize: function () {
      if (document.referrer) {
        var href = this.el.attr('href');

        // If the referrer (previous page) starts with the same as the link href
        // then update the link with the referrer, so any filters applied will be used
        // If there's no referrer, or the referrer doesn't match, then do nothing
        // The link will just go to the default view
        if (document.referrer.indexOf(href) >= 0) {
          var parsed_url = parseurl(document.referrer);

          // Get the view from the path - this code is getting the path of the iframe referrer - so we need to turn back into
          // the URL for the page itself - by parsing in view_id as a parameter
          var view = parsed_url.path.match(pattern);
          if (view) {
            parsed_url.qs['view_id'] = view[1];
          }

          // Loop through all the parameters, adding them to the href
          var conj = '?';
          $.each(parsed_url.qs, function (index, value) {
            href += conj + index + '=' + value;
            conj = '&';
          });

          this.el.attr('href', href);
          this.el.append('Back to resource');
          return;
        }
      }

      // If the referrer isn't the same (coming in from an external page), link should just be View Resource
      this.el.append('View resource');
    },
  };
});

/**
 * parseqs
 *
 * Parse a url's query string into path and qs components, where qs is a map of var name to value. Values are
 * not url decoded.
 */
function parseurl(url) {
  var parts = url.split('?');
  if (parts.length == 1) {
    return {
      path: parts[0],
      qs: {},
    };
  }
  var qs = {};
  var qs_parts = parts[1].split('&');
  for (var i = 0; i < qs_parts.length; i++) {
    var v_parts = qs_parts[i].split('=');
    var name = v_parts[0];
    var value = '';
    if (v_parts.length == 1) {
      value = 1;
    } else {
      value = v_parts[1];
    }
    if (qs[name]) {
      qs.name.push(value);
    } else {
      qs[name] = [value];
    }
  }
  return {
    path: parts[0],
    qs: qs,
  };
}
