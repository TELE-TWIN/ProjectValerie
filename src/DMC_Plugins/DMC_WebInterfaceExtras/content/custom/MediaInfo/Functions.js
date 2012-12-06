//
//MEDIAINFO
//

/*GLOBAL*/
var debug = false;

/*FUNCTIONS*/
$(document).ready(function(){
	
	/* parse values from URL */	
	var params = get_params();
	var mode = params["mode"];			// => done/edit/add/addbyimdb/change_imdbid
	var type = params["type"]; 			// => isMovie/isTvShow/isEpisode
	var Id = params["Id"]; 	
	var ParentId = params["ParentId"];
	var message = params["msg"];

	if (debug) {alert("area => mediainfo/function.js \nfnc => document ready " + "\nmode => " + mode + "\nId => " + Id + "\nParentId => " + ParentId + "\ntype => " + type);}
	
	//DONE SECTION
	if (mode == "showDoneForm") {
		window.alert("Changes have been sent. Please note that you have to save to database after finishing your changes!");
		
		var parameters = "";
		if (typeof(ParentId)!= 'undefined') {
			parameters = parameters +"&ParentId="+ParentId;
		}		
		if (typeof(Id) != 'undefined') {
			parameters = parameters +"&Id="+Id;
		}

		url = '/' + target + '?showSave=true'+parameters;
		if (debug) {alert("area => mediainfo/function.js \nfnc => document ready " + "\nurl => " + url);}
		window.open(url, '_self');
		return;
	
	} else if (mode == "showErrorForm") {
		window.alert("An Error ocurred :( ! \n\n" + message);
		return;
	
	//ADD NEW RECORD MANUAL
	} else if (mode == "showManualAddForm") {
		if (debug) {alert(mode);}
		$("#special_features").hide();
		
		changeTable(type);
		document.getElementById('type').value = params["type"];
		if (type == "isEpisode") {
			document.getElementById('ParentId').value = params["ParentId"];
		}
	
	//ADD NEW RECORD WITH DATA
	} else if (mode == "showAddByImdbForm") {
		$("#special_features").hide();
		$('[name=Id]').val(Id);
		$('[name=Id2]').val(Id);
		
		changeTable(type);
		
	
	// MANUAL EDIT OF AN EXISTING RECORD 
	} else if (mode == "showEditForm") {
		if (type != "isMovie") {
			$("#special_features").hide();
		}
		changeTable(type);
		
		$("#tr_imdbid").hide();
	
	//CHANGE EXISTING RECORD BY CHANGING IMDBID
	} else if (mode == "change_imdbid") {
		if (debug) {alert(mode);}
		//$('[name=what]').val(type);
		$('[name=oldImdbId]').val(params["oldImdbId"]);
		
		$("#special_features").hide();
		
		fillTable(params, usePath);
		changeTable(type);
		
		$("#tr_imdbid").hide();
	
	//SHOULD NOT HAPPEN :-)
	} else {
		alert("ERROR - no mode defined")
	}
});


function changeTable(table_type) {
	
	if (debug) {alert("area => mediainfo/function.js \nfnc => changeTable " + "\ntable_type => " + table_type);}
	
	if (table_type == "isMovie") {
		$('#tr_season').remove();
		$('#tr_episode').remove();
		$('#tr_thetvdbid').remove();
		$('#tr_tag').remove();
		$('#tr_partentid').remove();
	} else if (table_type == "isTvShow") {
		$('#tr_tag').remove();
		$('#tr_season').remove();
		$('#tr_episode').remove();
		$('#tr_popularity').remove();
		$('#tr_runtime').remove();
		$('#tr_path').hide();
		$('#tr_filename').hide();
		$('#tr_extension').hide();
		// dirty workaround until TvShow needs those information like a movie or episode
		document.getElementById('path').value = "/dummy/";
		document.getElementById('filename').value = new Date().getTime();
		document.getElementById('extension').value = "dmy";
		
	} else if (table_type == "isEpisode") {
		//for now nothing
	} else {
		alert("Error - no type found");
	}
}

function fillTable(params, usePath) {
	alert("i am still used")
	
	if (debug) {alert("area => mediainfo/function.js \nfnc => fillTable (functions.js) " + "\nparams => " + params + "\nusePath" + usePath);}
	
	/* fill complete structure with data */
	document.getElementById('type').value = params["type"];
	document.getElementById('id2').value = params["Id"]; /* debug only */
	document.getElementById('id').value = params["Id"];
	document.getElementById('imdbid').value = params["ImdbId"];
	document.getElementById('thetvdbid').value = params["TheTvDbId"];
	document.getElementById('title').value = params["Title"];
	document.getElementById('season').value = params["Season"];
	document.getElementById('episode').value = params["Episode"];
	document.getElementById('plot').value = params["Plot"];
	document.getElementById('runtime').value = params["Runtime"];
	document.getElementById('year').value = params["Year"];
	document.getElementById('genres').value = params["Genres"];
	document.getElementById('tag').value = params["Tag"];
	document.getElementById('popularity').value = params["Popularity"];
	if (usePath == "true") {
		document.getElementById('path').value = params["Path"];
		document.getElementById('filename').value = params["Filename"];
		document.getElementById('extension').value = params["Extension"];
	}

	if (params["type"] == "isMovie") {
		$("#duck_img").attr("src","/media/" + params["ImdbId"] + "_poster_195x267.png");
		$("#duck_backdrop_img").attr("src","/media/" + params["ImdbId"] + "_backdrop_320x180.png");
		
	} else if (params["type"] == "isTvShow" || params["type"] == "isEpisode") {
		$("#duck_img").attr("src","/media/" + params["TheTvDbId"] + "_poster_195x267.png");
		$("#duck_backdrop_img").attr("src","/media/" + params["TheTvDbId"] + "_backdrop_320x180.png");
	}
}

function showAlternatives() {
	if (debug) {alert("area => mediainfo/function.js \nfnc => showAlternatives " + "\nparams => none");}
	
	var reply = prompt("Please specify your search string or enter ImdbID e.g. tt1234567.", document.getElementById('title').value);
	if (reply == null) { return;} 
	
	/*if imdbid is provided skip searching for alternatives and fill data in mediainfo form*/
	if (reply.length == 9 & reply.match("tt") != null) {
		urlString = "/mediaForm?";
		urlString += "Id=" + document.getElementById('id2').value + "&";
		urlString += "type=isMovie&";
		urlString += "mode=showAddByImdbForm&";
		urlString += "ImdbId=" + reply;
		if (debug) {alert("area => mediainfo/function.js \nfnc => showAlternatives " + "\nurlString => " + urlString);}
	} else {
		urlString = "/alternatives?";
		urlString += "type=" + document.getElementById('type').value + "&";
		urlString += "Id=" + document.getElementById('id2').value + "&";
		urlString += "searchString=" + reply;
		if (debug) {alert("area => mediainfo/function.js \nfnc => showAlternatives " + "\nurlString => " + urlString);}
	}
	window.open(urlString, '_self');
}

function changePictures(media_type) {
	if (debug) {alert("area => mediainfo/function.js \nfnc => changePictures " + "\nmedia_type => " + media_type);}
	
	if (!debug) {
		var reply = prompt("Please specify URL or PATH to the picture.", "http://my.url or /path/to/picture.extension");
	} else {
		var reply = prompt("Please specify URL or PATH to the picture.", "http://img138.imageshack.us/img138/7311/iamlegendposter02.jpg");
	}
	var params = get_params();
	var type = params["type"];
	var parameter = new Array();
	
	parameter["mode"] = "changeMediaArts";
	
	if (media_type == "poster") {
		parameter["media_type"] = "poster";
	
	} else if (media_type == "backdrop") {
		parameter["media_type"] = "backdrop";
	
	} else {
		alert("no media type defined");
	}
	
	parameter["media_source"] = reply;
	parameter["type"] = type
	parameter["Id"] = params["Id"]
	
	//if (type == "isMovie") {
	//	parameter["ImdbId"] = params["ImdbId"];
	//		
	//} else if (type == "isTvShow") {
	//	parameter["TheTvDbId"] = params["TheTvDbId"];	
	//
	//} else if (type == "isEpisode") {
	//	parameter["TheTvDbId"] = params["TheTvDbId"];
	//	parameter["Season"] = params["Season"];	
	//	parameter["Episode"] = params["Episode"];
	//} else {
	//	alert("no primary key set");
	//}

	if (reply == null) { return;} 
	
	var data = "";
	for (param in parameter) {
		data += param + "=" +  encodeURIComponent(parameter[param]) + "&";
	}
	if (debug) {alert("area => mediainfo/function.js \nfnc => changePictures " + "\ndata => " + data);}

	$.ajax({
		url: "/action",
		type: "GET",
		data: data,
		success: function (returnCode) {
			if (returnCode== "success") {
				 location.reload();
			} else {
				alert('Error - Please try again');
			}
		}
	});
 }
