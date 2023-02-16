// define a closure for external links functionality, but only if it hasn't been defined
window.external_links =
  window.external_links ||
  (function () {
    var self = {};

    /**
     * Binds listeners to allow parents to be collapsed or opened to show the child elements on click.
     */
    self.bindCollapsible = function () {
      // start off with the children not visible
      $(document).find('.external-link-child').hide();
      $('.external-link-parent').click(function () {
        // hide all sibling's lists
        $(this).siblings('.external-link-parent').find('li').slideUp();
        // and toggle this ul's list
        $(this).find('li').slideToggle();
      });
    };

    return self;
  })();

// bind up as soon as the document is ready for it
$(document).ready(function () {
  window.external_links.bindCollapsible();
});
