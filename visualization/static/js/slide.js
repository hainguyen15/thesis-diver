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
			url: `${config.BASE_URL}${config.PROJECT_NAME}/${this._id}/tiles`,
			type: 'GET',
       		success: (data) => {
				this.tiles = data.tiles;
				itemId = this._id;
	            pubsub.publish("SLIDE", this);
				
	   			tileSource = {
	            	width: data.tiles.sizeX,
	                height: data.tiles.sizeY,
	                tileWidth: data.tiles.tileWidth,
	                tileHeight: data.tiles.tileHeight,
	                minLevel: 0,
					maxLevel: data.tiles.levels - 1,
	                getTileUrl: (level, x, y) => {
						return `${config.BASE_URL}${config.PROJECT_NAME}/${data.name}_files/${level}/${x}_${y}.jpeg`
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
