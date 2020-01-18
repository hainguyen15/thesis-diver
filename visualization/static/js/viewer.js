/* viewer.js

Description:
	This module initializes and defines the configurations for the Openseadragon
	viewer. Any additional configurations and event handlers should be added here.

Dependencies:
	- osd: Openseadragon module

Return:
	- viewer - Openseadragon viewer object
 */

define("viewer", ["osdImgHelper","osd", "pubsub","config", "scalebar"], function(oshIH, osd, pubsub,config, scalebar) {

    var viewer = osd({
        id: 'image_viewer',
        prefixUrl: "static/js/bower_components/openseadragon/built-openseadragon/openseadragon/images/",
        navigatorPosition: "BOTTOM_RIGHT",
        showNavigator: true
    });

    viewer.scalebar({
        xOffset: 10,
        yOffset: 10,
        barThickness: 3,
        color: '#555555',
        fontColor: '#333333',
        backgroundColor: 'rgba(255, 255, 255, 0.5)',
    });

      //this loads after the viewer is created..

    if ( config.MODULE_CONFIG["zoomButtons"] )  { require(["zoomButtons"])};

    return viewer;
});
