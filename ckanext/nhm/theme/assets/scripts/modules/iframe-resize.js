// Track iframe content height changes and resize element accordingly
this.ckan.module('iframe-resize', function (jQuery, _) {
  return {
    initialize: function () {
      var $iframe = this.el;
      $iframe.ready(function () {
        var i_window = $iframe.get(0).contentWindow;
        var set_height = function () {
          // body is not always available on some browsers. True even if we did a jQuery(i_window.document).ready(...)
          if (i_window.document && i_window.document.body) {
            // without Math.ceil it will constantly switch between pixel fractions and make the page twitch
            var current = Math.ceil($iframe.height());
            var target = Math.ceil(jQuery(i_window.document).height());
            if (current != target) {
              $iframe.height(target);
            }
          }
        };
        set_height();
        // This is, unfortunately, the only reliable cross browser way to track iframe size changes.
        jQuery(i_window).resize(set_height);
        window.setInterval(set_height, 250);
      });
    },
  };
});
