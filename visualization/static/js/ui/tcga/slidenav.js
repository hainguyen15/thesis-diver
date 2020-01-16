define("tcga/slidenav", ["config", "viewer", "pubsub", "slide", "jquery", "webix"], function(config, viewer, pubsub, slide, $) {

    webix.proxy.PagingGirderItems = {
      $proxy:true,
      load:function(view, callback, details){
        if (details){
          var data = webix.ajax(this.source+"?limit="+details.count+"&offset="+details.start);
        } else {
            var data = webix.ajax(this.source+"?limit=5&offset=0"); 
        }
         
        data.then((resp) => {
            webix.ajax.$callback(view, callback, resp.text());
        }); 
      }
    };

    var thumbnailsPanel = {
        view: "dataview",
        id: "thumbnails",
        select: true,
        template: "<div class='webix_strong'>#name#</div><img src='" + config.BASE_URL + "/item/#_id#/tiles/thumbnail'/>",
        pager: "item_pager",
        datafetch: 25,
        type: {
            height: 170,
            width: 200
        },
        on: {
            onItemClick: function(id, e, node) {
                var item = this.getItem(id);
                console.log(item);
                slide.init(item);
            },
            onAfterLoad: function(){
                if(this.getFirstId()){
                    var item = this.getItem(this.getFirstId());
                    slide.init(item);
                }
            },
            onAfterRender: webix.once(function() {
                $.get(config.BASE_URL + "/tcga/cohort", function(resp){
                    var cohorts = resp["data"];
                    // var cohortList = $$("slideset").getPopup().getList();
                    // cohortList.clearAll();
                    // cohortList.parse(cohorts);
                    // $$("slideset").setValue(cohorts[0].id);

                    var url = "PagingGirderItems->" + config.BASE_URL + "/tcga/cohort/" + cohorts[0]._id + "/images";
                    $$("thumbnails").clearAll();
                    $$("thumbnails").load(url); 
                });    
            })
        }
    };

    itemPager = {
        view:"pager",
        id: "item_pager",
        height:45,
        template: "<center>{common.prev()}{common.page()}/#limit#{common.next()}<br/>(#count# slides)</center>",
        animate:true,
        size:5,
        group:4
    };

    //dropdown for slide groups
    //Data is pulled from DAS webservice
    dropdown = {
        view: "combo",
        placeholder: "Select Cohort",
        id: "slideset",
        options: {
            body: {
                template: "#name#"  
            }
        },
        on: {
            onChange: function(id) {
                var item = this.getPopup().getBody().getItem(id);

                var url = "PagingGirderItems->" + config.BASE_URL + "/tcga/cohort/" + item._id + "/images";
                $$("thumbnails").clearAll();
                $$("thumbnails").setPage(0);
                $$("thumbnails").load(url);
             
                // $.get(config.BASE_URL + "/tcga/case?limit=2000&cohort=" + item._id, function(resp){
                //     var cases = resp["data"]
                //     var sFoldersMenu = $$("samples").getPopup().getList();
                //     $$("samples").setValue();
                //     sFoldersMenu.clearAll();
                //     sFoldersMenu.parse(cases);
                // });
            },
            // onAfterRender: webix.once(function() {
            //     $.get(config.BASE_URL + "/tcga/cohort", function(resp){
            //         var cohorts = resp["data"];
            //         // var cohortList = $$("slideset").getPopup().getList();
            //         // cohortList.clearAll();
            //         // cohortList.parse(cohorts);
            //         // $$("slideset").setValue(cohorts[0].id);

            //         var url = "PagingGirderItems->" + config.BASE_URL + "/tcga/cohort/" + cohorts[0]._id + "/images";
            //         $$("thumbnails").clearAll();
            //         $$("thumbnails").load(url); 
            //     });    
            // })
        }
    };

    // samples_dropdown = {
    //     view: "combo",
    //     placeholder: "Select Sample",
    //     id: "samples",
    //     options: {
    //         filter:function(item, value){
    //             if(item.name.toString().toLowerCase().indexOf(value.toLowerCase()) > -1)
    //               return true;
    //             return false;
    //         },
    //         body: {
    //             template: "#name#"
    //         }
    //     },
    //     on: {
    //         onChange: function(id) {
    //             if(id){
    //                 var item = this.getPopup().getBody().getItem(id);
    //                 var thumbs = $$("thumbnails");
    //                 var url = config.BASE_URL + "/tcga/case/" + item._id + "/images";
    //                 thumbs.clearAll();
    //                 thumbs.setPage(0);
    //                 thumbs.load(url);
    //             }
    //         }
    //     }
    // };

    //slides panel is the left panel, contains two rows 
    //containing the slide group dropdown and the thumbnails panel 
    var wideIcon = "<span class='aligned wide webix_icon fa-plus-circle'></span>";
    var narrowIcon = "<span class='aligned narrow webix_icon fa-minus-circle'></span>";
    var slidesPanel = {
        id: "slidenav",
        header: "Slides " + wideIcon + narrowIcon,
        onClick:{
            wide: (event, id) => {
                var count = $$("thumbnails").count();
                this.config.width = 205*6;
                this.resize();

              $$("item_pager").config.size = Math.min(30, count);
              $$("item_pager").refresh();
              $$("thumbnails").refresh();
              return false;
            }, 
            narrow: (event, id) => {
              this.config.width = 220;
              this.resize();

              $$("item_pager").config.size = 5;
              $$("item_pager").refresh();
              $$("thumbnails").refresh();
              return false;
            }
        },
        body: {
            rows: [
                thumbnailsPanel, itemPager
                // thumbnailsPanel
            ]
        },
        width: 220
    };


    return slidesPanel;
});
