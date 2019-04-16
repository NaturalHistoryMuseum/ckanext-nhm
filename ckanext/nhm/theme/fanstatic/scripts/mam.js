/**
 * Created by bens3 on 07/11/15.
 */

var MAM = {
    config : {
        endpoint: '/api/3/action/download_image',
        formTpl: '<form id="mam"><p><small>Please enter your email address, and we will send you the original image.</small></p><input type="hidden" value="{{resource_id}}" name="resource_id"><input type="hidden" name="record_id" value="{{record_id}}"><input type="hidden" name="asset_id" value="{{asset_id}}"><div class="input-append"><input type="email" class="input-large" name="email" value="" required placeholder="Email address" oninvalid="this.setCustomValidity(\'Please enter your email\')" oninput="setCustomValidity(\'\')"><button type="submit" class="btn btn-success"><i class="icon-circle-arrow-right icon-large"></i></button></div><hr><p><small><i>Data Protection</i></small></p><p><small>The Natural History Museum will use your personal data in accordance with data protection legislation to process your requests. For more information please read our <a href="/privacy">privacy notice</a>.</small></p></form>'
    },

    init : function() {

        $('#download-tooltip').tooltip({
            position: { of: '#blueimp-gallery a.gallery-control-download', my: 'left+60 center', at: 'left center' },
            tooltipClass: "download-tooltip"
        });
        var $gallery = $('#blueimp-gallery')
        $gallery.find('a.gallery-control-download').on('click', jQuery.proxy(MAM._hijackDownloadLink));
        // Hide the tooltip if the gallery is clicked
        $gallery.on('click', jQuery.proxy(MAM._hideDownloadTooltip));

    },
    _hijackDownloadLink: function(e){
        // Take over the download link - if it's a MAM one show the tooltip options
        // Otherwise just propagate to default action
        var image = $('#blueimp-gallery').data('image')
        if(image.href.indexOf('nhm.ac.uk/services/media-store/asset') != -1){
            MAM._showDownloadTooltip(image)
            e.stopPropagation()
            return false
        }
        return true
    },

    _showDownloadTooltip: function(image){
        // Get the HTML image 0 we then know the dimensions
        $img = $('#blueimp-gallery img[src="' + image.href + '"]')

        $('#download-tooltip').tooltip({open: function( event, ui ) {
            var ul = $('<ul/>')
            $('<li><a href="' + image.href + '" download>Download image (' + $img[0].naturalHeight + '&times;' + $img[0].naturalWidth + ')</a></li>').appendTo(ul);

            $('<li/>').append($('<a>',{
                text: 'Download original image (hi-res)',
                title: 'Download original image',
                href: '#',
                click: function(e){
                    // If mam form is visible, add the active class to the link
                    // Add here - if we use the toggle callback, there's a pause in display
                    e.preventDefault();
                    $(e.target).toggleClass('active', $('#mam').not(":visible"))
                    $('#mam').toggle();
                    return false;

                }
            })).appendTo(ul);

            // create a context for rendering the mustache form template
            let mustacheContext = {
                resource_id: image.resource_id,
                record_id: image.record_id,
            };

            // if we can find an asset ID in the image url, add it to the context
            let match = /asset\/([a-z0-9]+)\//.exec(image.href);
            if (match != null) {
                mustacheContext.asset_id = match[1];
            }

            // render the form
            let form = Mustache.render(MAM.config.formTpl, mustacheContext);

            $(ui.tooltip).html(ul.append(form));

            // Handle form submission
            $('form', ui.tooltip).submit(function( e ) {

                var self = $(this)
                $(this).addClass('working')
                // Map form values to data object
                var data = {};
                $(this).serializeArray().map(function(x){data[x.name] = x.value;});
                $.ajax({
                   type: "POST",
                   url: MAM.config.endpoint,
                   data: JSON.stringify(data), // serializes the form's elements.
                   complete: function(){
                       $(this).removeClass('working')
                   },
                   error: function(){
                       self.html('<p class="result"><small><i class="icon-exclamation-sign" aria-hidden="true"></i> Sorry we could not complete your request at this time - please try again later.</small></p>')
                   },
                   success: function(){
                       self.html('<p class="result"><small>Thank you - you will receive a confirmation email shortly.</small></p>')
                   }
                });
              e.preventDefault();
            });

            }
        }).tooltip( "open" )

    },
    _hideDownloadTooltip: function(e){
        $('#download-tooltip').tooltip('close');
    }
};

$(document).ready(function() { MAM.init(); });

