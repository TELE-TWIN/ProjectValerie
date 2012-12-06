$(document).ready(function(){

	var isRunning = $('#isRunning').val();

	if (isRunning == "False") { 
		$("#cancelSync").hide();
		$("#normalSync").show();
		$("#fastSync").show();		
	} else {
		$("#cancelSync").show();
		$("#normalSync").hide();
		$("#fastSync").hide();
	    
	   startLogViewClass();
	}
});

function startLogViewClass() {
	//global
	var finished = "";
 	
 	$("#uploadprogressbar").progressBar();
	$("#uploadprogressbar").fadeIn();
 	
 	//first run
 	showSyncProgress();
	showSyncLog();

    //first + n run until we detect finish
    var myTimer = setInterval(function() {
    							getState();
						        showSyncProgress();
								showSyncLog();
								if (finished == "True") {
									clearInterval(myTimer);
									$("#cancelSync").hide();
									$("#normalSync").show();
									$("#fastSync").show();	
									}
						    	}, 1000);


	function getState() {
		dmurl = document.location.host;
		
		$.ajax({
			  url : "http://" + dmurl + "/syncronize?mode=getFinishedState",
			  context: document.body,
			  async: false,
			  success: function(state){
					finished = state;
			  	}
			});
	}

	function showSyncLog() {
		dmurl = document.location.host;
		var i=0;
		for (i=0;i<=41;i++) { //because we have 40 lines of log
			$.ajax({
			  url : "http://" + dmurl + "/syncronize?mode=getSyncLog&row=" + i,
			  context: document.body,
			  async: false,
			  success: function(data){
				$("#logrow" + i).text(data);
			  	}
			});
		}
	}




	function showSyncProgress() {
		dmurl = document.location.host;
		
		$.ajax({
			  url : "http://" + dmurl + "/syncronize?mode=getSyncPercentage",
			  context: document.body,
			  async: false,
			  success: function(percentage){
				$("#uploadprogressbar").progressBar(percentage);
			  	}
			});
	}


}
