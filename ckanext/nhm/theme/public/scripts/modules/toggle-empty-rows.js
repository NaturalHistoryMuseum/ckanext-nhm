/* Table toggle more
 * When a table has more things to it that need to be hidden and then shown more
 */
this.ckan.module('toggle-empty-rows', function($, _) {
  return {

    /* Initialises the module setting up elements and event listeners.
     *
     * Returns nothing.
     */
    initialize: function () {
      $('<a href="#" class="toggle-empty-rows">Toggle empty rows</a>').on('click', {tbl: this.el}, this._toggleDisplay).insertBefore(this.el)
    },

    _toggleDisplay: function(e) {
      e.preventDefault();
        e.data.tbl.toggleClass('table-hide-empty');
    }

  }
});
