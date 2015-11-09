/**
 * Created by bens3 on 07/11/15.
 */

$(function() {

    var endpoint = 'http://127.0.0.1:8000/api/3/action/download_image'
    var tpl = '<form id="mam"><p><small>Please enter your email address, and we will send you the original image.</small></p><input type="hidden" value="{{resource_id}}" name="resource_id"><input type="hidden" name="record_id" value="{{record_id}}"><input type="hidden" name="asset_id" value="{{asset_id}}"><div class="input-append"><input type="email" class="input-large" name="email" value="" required placeholder="Email address" oninvalid="this.setCustomValidity(\'Please enter your email\')" oninput="setCustomValidity(\'\')"><button type="submit" class="btn btn-success"><i class="icon-circle-arrow-right icon-large"></i></button></div></form>'

    $("#blueimp-gallery").on( "tooltipopen", function( event, ui ) {

        var image = $('#download-tooltip').data("image")

        console.log(image);

        // If this is a MAM image, add the MAM download form
        if(image.href.indexOf('nhm.ac.uk/services/media-store/asset')){

            var form = Mustache.render(tpl, {
                resource_id: image.resource_id,
                record_id: image.record_id,
                asset_id: image.href.replace("http://www.nhm.ac.uk/services/media-store/asset/", "").replace("/contents/preview", "")
            })

            var li = $('<li/>')

            $('<a>',{
                text: 'Download original image (hi-res)',
                title: 'Download original image',
                href: '#',
                click: function(e){
                    // If mam form is visible, add the active class to the link
                    // Add here - if we use the toggle callback, there's a pause in display
                    $(e.target).toggleClass('active', $('#mam').not(":visible"))
                    $('#mam').toggle();
                    e.preventDefault();
                    return false;
                }
            }).appendTo(li);

            $('ul', ui.tooltip).append(li).append(form);

            // Handle form submission
            $('form', ui.tooltip).submit(function( e ) {

                var self = $(this)
                $(this).addClass('working')
                // Map form values to data object
                var data = {};
                $(this).serializeArray().map(function(x){data[x.name] = x.value;});
                $.ajax({
                   type: "POST",
                   url: endpoint,
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





    } );

});

