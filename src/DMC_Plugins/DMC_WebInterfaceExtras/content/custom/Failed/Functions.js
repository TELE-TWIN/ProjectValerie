$(document).ready(function(){
	document.title = document.title + " - Failed";
	var params = get_params();
	$('#main_table').dataTable( {
		"aaSorting": [[ 1, "asc" ]],
		"bJQueryUI": true,
		"sPaginationType": "full_numbers",
		"sScrollY": "",
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
		<!-- PAGINATION_FLAG --> 
		iDisplayStart: 0,
	} );

	if (params["showSave"] != "true") {
		$('#sm_save').hide();
	}
});
