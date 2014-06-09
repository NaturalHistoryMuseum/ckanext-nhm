/* Loads the Image into a modal dialog.
 *
 * Examples
 *
 *   <a data-module="modal-image"">Image</a>
 *
 */
this.ckan.module('modal-image', function (jQuery, _) {
  return {

    /* holds the loaded lightbox */
    modal: null,

    options: {
      imageUrl: null,
      template: [
        '<div class="modal">',
        '<button type="button" data-dismiss="modal" class="close" style="z-index: 100; position:absolute; top:0; right:2px; line-height: 16px;">×</button>',
        '<div class="modal-body" style="max-height:600px!important"></div>',
        '</div>'
      ].join('\n')
    },

    /* Sets up event listeners
     *
     * Returns nothing.
     */
    initialize: function () {
      jQuery.proxyAll(this, /_on/);
      this.el.on('click', this._onClick);
    },

    /* Displays the image
     *
     */
    show: function () {
        this.sandbox.body.append(this.createModal());
        this.modal.modal('show');
    },

    /* Hides the modal.
     *
     */
    hide: function () {
      if (this.modal) {
        this.modal.modal('hide');
      }
    },

    /* Creates the modal dialog
     * And adds the image
     */
    createModal: function () {
      if (!this.modal) {
        var element = this.modal = jQuery(this.options.template);
        element.modal({show: false});
        element.find('.modal-body').prepend('<img src="'+this.options.imageUrl+'" />')
      }
      return this.modal;
    },

    /* Event handler for clicking on the element */
    _onClick: function (event) {
      event.preventDefault();
      this.show();
    },

  };
});
