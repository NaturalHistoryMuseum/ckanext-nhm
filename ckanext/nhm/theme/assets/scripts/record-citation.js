// define a closure for external links functionality, but only if it hasn't been defined
window.record_citations =
  window.record_citations ||
  (function () {
    var self = {};

    /**
     * Find the elements we needa nd bind hover listeners to them.
     */
    self.bind = function () {
      self.element = $(document).find('#citation-info');
      self.info = $(document).find('#citation-info-popup');
      self.info.hide();
      self.element.hover(self.enter, self.exit);
    };

    self.enter = function () {
      var elementPosition = self.element.position();
      // make sure the info box is positioned next to the info icon
      self.info.css({
        top: elementPosition.top,
        left: elementPosition.left + self.element.width() + 15,
      });
      self.info.show();
    };

    self.exit = function () {
      self.info.hide();
    };

    return self;
  })();

// bind up as soon as the document is ready for it
$(document).ready(function () {
  window.record_citations.bind();
});
