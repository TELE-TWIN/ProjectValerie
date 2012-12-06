$(document).ready(function(){ 
	document.title = document.title + " - Movies";
	var params = get_params();
	var message = params["msg"];

	$('#main_table').dataTable( {
		"aaSorting": [[ 1, "asc" ]],
		"bJQueryUI": true,
		"sPaginationType": "full_numbers",
		"sScrollY": "",
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
		<!-- PAGINATION_FLAG --> 
		iDisplayStart: 0,
	} );

	if (params["mode"] == "error") {
			window.alert("An Error ocurred :( \n\n" + message);
		return;
	}	

	if (params["showSave"] != "true") {
		$('#sm_save').hide();
	}
	else
	{
		window.setInterval ( "blink('#sm_save')", 1500 );
	}

});

function stream (mediaId, mediaType) {
	url = "http://" + document.location.host + "/mediaForm?mode=getMediaDetails&Id=" + mediaId + "&type=" + mediaType;
	dmurl = document.location.host;
	dmurl = dmurl.substring(0,dmurl.length-5);
	jQuery.ajax({
	  url: url,
	  context: document.body,
	  success: function(data){
		window.open("http://" + dmurl + "/web/ts.m3u?file=" + data, "_blank");
	  }
	});
}

function play (mediaId, mediaType) {
	url = "http://" + document.location.host + "/mediaForm?mode=getMediaDetails&Id=" + mediaId + "&type=" + mediaType;
	dmurl = document.location.host;
	dmurl = dmurl.substring(0,dmurl.length-5);
	jQuery.ajax({
	  url: url,
	  context: document.body,
	  success: function(data){
			serviceRef = "4097%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A"
			zap("http://" + dmurl + "/web/zap?sRef=" + serviceRef + data);
	  }
	});
}

function zap(url){
	alert(url);
	jQuery.ajax({
	  url: url,
	  context: document.body,
	  success: function(){
		//nothing to do for now;
	  }
	});
}
		
function download (mediaId, mediaType) {
	url = "http://" + document.location.host + "/mediaForm?mode=getMediaDetails&Id=" + mediaId + "&type=" + mediaType;
	dmurl = document.location.host;
	dmurl = dmurl.substring(0,dmurl.length-5);
	jQuery.ajax({
	  url: url,
	  context: document.body,
	  success: function(data){
		window.open("http://" + dmurl + "/file?file=" + data, "_blank");
	  }
	});
}
