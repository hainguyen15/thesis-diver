require = {
    urlArgs: "bust=" + (+new Date),
    paths: {
        "signals": "static/js/bower_components/js-signals/dist/signals.min",
        "d3": "static/js/bower_components/d3/d3.min",
        "osd": "static/js/bower_components/openseadragon/built-openseadragon/openseadragon/openseadragon.min",
        "geo": "static/js/bower_components/geojs/geo",
        "webix": "static/js/bower_components/webix/codebase/webix",
        "jquery": "static/js/bower_components/jquery/dist/jquery.min",
        "pubsub": "static/js/bower_components/PubSubJS/src/pubsub",
        "config": "static/js/config",
        "slide": "static/js/slide",
        "viewer": "static/js/viewer",
        "app": "static/js/app",
        "filters": "static/js/plugins/filters",
        "pathology": "static/js/plugins/pathology",
        "metadata": "static/js/plugins/metadata",
        "annotations": "static/js/plugins/annotations",
        "Hammer": "static/js/bower_components/hammerjs/hammer",
        "simpleMultiViewerHelper": "static/js/simpleMultiViewerHelper",
        "osdFilters": "static/js/externalJS/openseadragon-filtering",
        "osdImgHelper": "static/js/bower_components/openseadragon-imaginghelper/index",
        "scalebar": "static/js/lib/openseadragon-scalebar"
    },

    shim: {
        "osdFilters": ["osd"],
        "scalebar": ["osd"],
        "common": ["login"],
    },

    packages: [{
            name: "ui",
            location: "static/js/ui"
        },
        {
            name: "tcga",
            location: "static/js/ui/tcga"
        },
        {
            name: "common",
            location: "static/js/ui/common"
        },
    ]
};