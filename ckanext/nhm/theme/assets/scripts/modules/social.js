/*
 * Turns CKAN's social links into pop up windows - except for the
 * copy-link button which copies the current URL to clipboard
 */
this.ckan.module('social', function ($, _) {
  return {
    initialize: function () {
      self = this;
      $('a', this.el).each(function () {
        // Check if the link is the copy text link
        if ($(this).data('copy-text') !== undefined) {
          $(this).on('click', self._on_copy_click);
        } else {
          $(this).on('click', self._on_click);
        }
      });
    },

    _on_click: function (e) {
      e.preventDefault();
      window.open(this.href, this.title, 'width=600,height=400');
      return false;
    },

    _on_copy_click: function (e) {
      e.preventDefault();
      // Get the URL from the element
      var url = $(this).data('copy-text');
      // Get the original text
      var $link = $(this);
      var original_text = $link.html();
      // Add the URL to the clipboard
      navigator.clipboard
        .writeText(url)
        .then(function () {
          // Display a success message
          $link.text('Link copied!');
          // Reset message after moment
          setTimeout(function () {
            $link.html(original_text);
          }, 1500);
        })
        .catch(function (err) {
          console.error(err);
        });

      return false;
    },
  };
});
