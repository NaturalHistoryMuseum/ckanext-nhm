$(document).ready(function () {
  // strip whitespace from buttons because that is not how we space things
  $('a.btn').each((i, el) => {
    var element = $(el);
    var children = element.contents();
    var html = children.map((i, child) => {
      if (child.nodeType === 3) {
        child.nodeValue = child.nodeValue.trim();
      }
      return child;
    });
    element.html(html);
  });

  // add the .no-txt class to every button with no text
  $('.btn:not(.no-txt), button:not(.no-txt)')
    .filter((i, b) => {
      let innerText = $(b.childNodes)
        .filter((i, el) => !$(el).hasClass('sr-only'))
        .text()
        .trim();
      return innerText === '';
    })
    .addClass('no-txt');

  // add the .no-icon class to every button with no icon
  $('.btn:not(.no-icon), button:not(.no-icon)')
    .filter((i, b) => {
      let btn = $(b);
      return btn.has('i').length === 0;
    })
    .addClass('no-icon');

  // fix some fontawesome references
  function replaceClass(oldClass, newClass) {
    $('.' + oldClass)
      .removeClass(oldClass)
      .addClass(newClass);
  }
  replaceClass('fa-cloud-upload', 'fa-cloud-upload-alt');
  replaceClass('fa-arrows', 'fa-arrows-alt-v');

  // fix the tabs problem
  var currentUrl = window.location.href;
  $('.nav-tabs li').map((i, el) => {
    var element = $(el);
    if (element.find('a').filter((j, a) => a.href === currentUrl).length > 0) {
      element.addClass('active');
    }
  });
});
