/* ui/main.js

Description:
    This module renders the UI. It combines the different UI components
    returned from the submodules and renders one UI.

Dependencies:
    - header: header component
    - filters: filters components used to control the brightness/contrast, etc. of the slide
    - slidenav: the left panel that contains the thumbnails, dropdown and search
    - toolbar: contains additional buttons setting on top the slide

Return:
    - viewer - Openseadragon viewer object
 */

define("tcga/main", ["tcga/slidenav", "common/toolbar", "common/header", "common/footer", "pubsub", "webix"], function(slidenav, toolbar, header, footer, pubsub) {

    pubsub.subscribe("SLIDE", function(msg, slide) {
        $$("metadata_list").clearAll();
        meta = []
        $.each(slide.tiles, function(key, val){
            meta.push({"key": key, "value": val});
        })

        $$("metadata_list").parse(meta);
    });

    rightPanelStub = {
                multi:true,
                view:"accordion",
                gravity: 0.3,
                id: "rightPanelStub",
                collapsed: false,
                cols:[
                    { 
                        header: "Image properties",  id: "tcgaRightAccordion",
                        body: {   
                            view: "datatable", 
                            select:"row",
                            id: "metadata_list",
                            columns:[
                                { id: "key", header: "Key", width: 150},
                                { id: "value", header: "Value", fillspace:true}
                            ]
                        }
                    }
                ]
            };


    function init() {
        //This is the Openseadragon layer
        viewerPanel = {
            id: "viewer_root",
            borderless: true,
            rows: [
                toolbar,
                {
                    id: "viewer_body",
                    cols: [
                        { view: "template", id: "viewer_panel", content: "geo_osd" },
                    ]
                }
            ]
        };
        //properties for dynamic edits are $$("tcgaRightPanel).define("width", 300) and then $$("tcgaRightPanel").resize();
        //Render the main layout
        //It contains the header, slidenav, Openseadragon layer
        webix.ui({
            container: "main_layout",
            id: "root",
            rows: [
                header, {
                    id: "mainSlidePanel", 
                    cols: [
                        slidenav, {
                            view: "resizer"
                        },
                        {

                            rows: [
                                viewerPanel,
                                footer
                            ]
                        },
                        rightPanelStub
                    ]
                }
            ]
        });
    }

    return {
        init: init
    }
});
