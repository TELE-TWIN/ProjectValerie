$(document).ready(function(){
	var debug = false;
	
	/* parse values from URL */	
	var params = get_params();
	
	$("#form1_type").val(params["type"]);
	$("#form2_type").val(params["type"]);
	$("#form3_type").val(params["type"]);
	
	if (debug) {alert(params["type"]);}

	if (params["type"] == "isMovie") {
		$("#header").html("Movie");
	
	} else if (params["type"] == "isTvShow") {
		$("#header").html("TvShow");
		//for now we romove them because thoes functions are not implemented
		$("#form1").remove();
		$("#form2").remove();
		
	} else if (params["type"] == "isEpisode") {
		$("#header").html("Episode");
		$("#ParentId").val(params["ParentId"]);
		
		//for now we romove them because thoes functions are not implemented
		$("#form1").remove();
		$("#form2").remove();
		/*
		$("#form1_idName").html("TheTvDbId");
		$("#form1_explain").html("(e.g. 123456)");
		$("#form1_idType").attr("name","TheTvDbId");
		$("#form1_submit").val("by TheTvDbId");
		*/
	} else {
		alert("Error - no type in params");
	}
});

