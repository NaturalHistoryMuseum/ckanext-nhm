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

    // add the .no-collapse class to every button with no text or no icon
    $('.btn:not(.no-collapse), button:not(.no-collapse)').filter((i, b) => {
        let btn = $(b);
        let innerText = $(b.childNodes).filter((i,el) => !$(el).hasClass('sr-only')).text().trim();
        if (btn.has('i').length === 0){
            return true;
        }
        else return innerText === '';
    }).addClass('no-collapse');

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