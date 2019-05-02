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
    $('.fa-cloud-upload').removeClass('fa-cloud-upload').addClass('fa-cloud-upload-alt');
});