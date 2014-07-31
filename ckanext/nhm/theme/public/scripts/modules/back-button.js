/* Table toggle more
 * When a table has more things to it that need to be hidden and then shown more
 */
this.ckan.module('back-button', function($, _) {

  return {

    /* Initialises the module setting up elements and event listeners.
     *
     * Returns nothing.
     */
    initialize: function () {

      if (document.referrer){
          var href = this.el.attr('href');

          // If the referrer (previous page) starts with the same as the link href
          // then update the link with the referrer, so any filters applied will be used
          // If there's no referrer, or the referrer doesn't match, then do nothing
          // The link will just go to the default view
          if (document.referrer.indexOf(href) >= 0){
              this.el.attr('href', document.referrer);
          }
      }

    }

  }
});
