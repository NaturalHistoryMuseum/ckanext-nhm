/**
 * Created by bens3 on 07/11/15.
 *
 * JH (12/10/21): This no longer uses MAM to download images! Will refactor once confirmed as
 * stable.
 */

var MAM = {
  init: function () {
    $('#download-tooltip').tooltip({
      position: {
        of: '#blueimp-gallery a.gallery-control-download',
        my: 'left+60 center',
        at: 'left center',
      },
      tooltipClass: 'download-tooltip',
    });
    var $gallery = $('#blueimp-gallery');
    $gallery
      .find('a.gallery-control-download')
      .on('click', jQuery.proxy(MAM._hijackDownloadLink));
    // Hide the tooltip if the gallery is clicked
    $gallery.on('click', jQuery.proxy(MAM._hideDownloadTooltip));
  },
  _hijackDownloadLink: function (e) {
    // Take over the download link - if it's a MAM one show the tooltip options
    // Otherwise just propagate to default action
    var image = $('#blueimp-gallery').data('image');
    if (!!image.download) {
      window.location = image.download;
      e.stopPropagation();
      return false;
    }
    return true;
  },
};

$(document).ready(function () {
  MAM.init();
});
