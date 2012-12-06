$(document).ready(function(){
	document.title = document.title + " - Series";
	var params = get_params();
	var i = 1,timer;
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
