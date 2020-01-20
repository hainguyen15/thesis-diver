define("common/header", ["config"], function(config) {
    
    var menu = {
        view:"menu",
        width: 250,
        id: "header_menu",
        data: [
        ],
        type:{height:15},
        css: "menu"
    };

    header = {
        borderless: true,
        cols: [{
            view: "toolbar",
            height: 1,
            css: "toolbar",
            cols: [{
                    view: "template",
                    borderless: true,
                    template: "<img src='" + config.LEFT_HEADER_IMG + "' height='40'/>",
                    width: 200
                }, 
                {},
                {
                    rows:[
                        menu,
                        {
                            view: "template",
                            align: "right",
                            borderless: true,
                            template: "<img src='" + config.RIGHT_HEADER_IMG + "' height='50'/>",
                            width: 250
                        }
                    ]
                },
            ]
        }]
    };

    return header;
});