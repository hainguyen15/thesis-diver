define("slide", ["viewer", "config", "pubsub", "scalebar"], function(viewer, config, pubsub, scalebar){

	function init(item){
		$.extend(this, item);
		this.item = item;
		
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
				var mpp = (data.tiles.mm_x + data.tiles.mm_y) / 2
				viewer.scalebar({
					pixelsPerMeter: mpp ? (1e6 / mpp) : 0
				});
	        }
		});
	}

	return{
		init: init
	}
})
