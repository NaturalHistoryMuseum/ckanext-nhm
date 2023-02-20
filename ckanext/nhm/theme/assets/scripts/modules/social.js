/*
 * Turns CKAN's social links into pop up windows
 */
this.ckan.module('social', function ($, _) {
  return {
    /* Initialises the module setting up elements and event listeners.
     *
     * Returns nothing.
     */
    initialize: function () {
      self = this;
      $('a', this.el).each(function () {
        $(this).on('click', self._on_click);
      });
    },

    _on_click: function (e) {
      e.preventDefault();
      window.open(this.href, this.title, 'width=600,height=400');
      return false;
    },
  };
});
