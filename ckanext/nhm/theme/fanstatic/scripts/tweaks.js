$(document).ready(function() {

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

    // fix some fontawesome references
    function replaceClass(oldClass, newClass) {
        $('.' + oldClass).removeClass(oldClass).addClass(newClass);
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
    })
});