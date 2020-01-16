require = {
    urlArgs: "bust=" + (+new Date),
    paths: {
        "fabric": "static/js/bower_components/fabric.js/dist/fabric.min",
        "osdfabric": "static/js/bower_components/OpenseadragonFabricjsOverlay/openseadragon-fabricjs-overlay",
        "hasher": "static/js/bower_components/hasher/dist/js/hasher.min",
        "signals": "static/js/bower_components/js-signals/dist/signals.min",
        "crossroads": "static/js/bower_components/crossroads/dist/crossroads.min",
        "d3": "static/js/bower_components/d3/d3.min",
        "svg": "static/js/bower_components/svg-overlay/openseadragon-svg-overlay",
        "osd": "static/js/bower_components/openseadragon/built-openseadragon/openseadragon/openseadragon.min",
        "geo": "static/js/bower_components/geojs/geo",
        "webix": "static/js/bower_components/webix/codebase/webix",
        "jquery": "static/js/bower_components/jquery/dist/jquery.min",
        "pubsub": "static/js/bower_components/PubSubJS/src/pubsub",
        "config": "static/js/config",
        "slide": "static/js/slide",
        "viewer": "static/js/viewer",
        "routes": "static/js/routes",
        "app": "static/js/app",
        "aperio": "static/js/plugins/aperio",
        "filters": "static/js/plugins/filters",
        "pathology": "static/js/plugins/pathology",
        "metadata": "static/js/plugins/metadata",
        "annotations": "static/js/plugins/annotations",
        "derm": "static/js/plugins/derm",
        "login": "static/js/login",
        "session": "static/js/session",
        "Hammer": "static/js/bower_components/hammerjs/hammer",
        "slideDetails": "static/js/plugins/slideDetails",
        "simpleAnnotationPanel": "static/js/plugins/simpleAnnotationPanel",
        "thumbLabeler": "static/js/plugins/thumbLabeler",
        "simpleMultiViewerHelper": "static/js/simpleMultiViewerHelper",
        "osdFilters": "static/js/externalJS/openseadragon-filtering",
        "osdImgHelper": "static/js/bower_components/openseadragon-imaginghelper/index",
        "folderMetadata": "static/js/plugins/folderMetadata",
        "zoomButtons": "static/js/plugins/zoomButtons",
        "tagger": "static/js/plugins/tagger"

    },

    shim: {
        "osdFilters": ["osd"],
        "svg": ["osd"],
        "common": ["login"],
        "osdImgHelper": ["osd", "svg"]

    },

    packages: [{
            name: "ui",
            location: "static/js/ui"
        },
        {
            name: "standard",
            location: "static/js/ui/standard"
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