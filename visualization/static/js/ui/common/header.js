define("common/header", ["login", "session", "config"], function(login, session, config) {
    
    if(session.valid())
        loginBtn = { id:"login_btn", value:"Logout (" + session.username() + ")"}
    else
        loginBtn = { id:"login_btn", value:"Login"}

    var menu = {
        view:"menu",
        width: 250,
        id: "header_menu",
        data: [
            loginBtn,
            { id:"1",value:"TCGA Resources", submenu:[
                 {value:"TCGA Analytical Tools", href: "https://tcga-data.nci.nih.gov/docs/publications/tcga/", target:"_blank"},
             ]},
            { id:"3",value:"Help", submenu:[
                {value:"About the CDSA"},
                {value:"Repository Stats"}
            ]}
        ],
        type:{height:15},
        css: "menu",
        on:{ 
            onItemClick:function(id){
                if(id == "login_btn"){
                    var val = $$('header_menu').config.data[0].value;
                    val == "Login" ? $$("login_window").show() : login.logout();
                }
            }
        }
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