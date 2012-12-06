$(document).ready(function(){
	var params = get_params();
	$('#main_table').dataTable( {
		"sScrollY": 768,
		"aaSorting": [[ 0, "desc" ]],
		"bScrollInfinite": true,
		"bPaginate": false,
		"bJQueryUI": true,
		"sPaginationType": "full_numbers"
	} );
});
