define("slide", ["viewer", "config", "pubsub"], function(viewer, config, pubsub){

	function init(item){
		$.extend(this, item);
		this.item = item;

		// if($$("footer") != undefined){
		// 	$$("footer").define("data",{
		// 		name: this.item.name,
		// 		url: "http://adrc.digitalslidearchive.emory.edu/dsa_base/#slide/" + this.item._id
		// 	});
		// }
		
       	$.ajax({
       		context: this,
			//    url: config.BASE_URL + "/item/" + this._id + "/tiles",
			// url: `${config.BASE_URL}/01_01_0083/tiles`,
			url: "http://localhost:5000/01_01_0083/tiles",
			type: 'GET',
       		success: (data) => {
				this.tiles = data;
				itemId = this._id;
	            pubsub.publish("SLIDE", this);
				
	   			tileSource = {
	            	width: data.sizeX,
	                height: data.sizeY,
	                tileWidth: data.tileWidth,
	                tileHeight: data.tileHeight,
	                minLevel: 0,
					maxLevel: data.levels - 1,
	                getTileUrl: (level, x, y) => {
						// return `${config.BASE_URL}/item/${itemId}/tiles/zxy/${level}/${x}/${y}?edge=crop`;
						return `http://localhost:5000/01_01_0083.svs_files/${level}/${x}_${y}.jpeg`
	            	}
	    		};

	        	viewer.open(tileSource);
	        }
		});
	}

	return{
		init: init
	}
})
