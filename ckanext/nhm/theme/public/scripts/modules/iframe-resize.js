// Track iframe content height changes and resize element accordingly
this.ckan.module('iframe-resize', function(jQuery, _) {
  return {
    initialize: function() {
      var $iframe = this.el;
      var i_window = $iframe.get(0).contentWindow;
      var i_doc = i_window.document;
      jQuery(i_window).resize(function(){
        $iframe.height(jQuery(i_doc).height);
      });
    }
  }
});
