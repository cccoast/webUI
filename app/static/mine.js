
$(document).ready(function(){

	function queryBacktestReady(){
		var ret = 0;
		alert("me");
	    $.ajax({
		  url: $SCRIPT_ROOT + '/auth/qeury_backtest_result',
		  data: {},
		  async: false,
		  dataType: 'json',
		  success: function (result) {
		    ret = result.result;
		  }
		});
		return ret;
	};
	
	function startTimer(duration) {
	    var exp_timer = duration * 2;
	    var refresh = setInterval(function () {
	    	alert("exp_timer");
		    var ret = queryBacktestReady();
		    if (ret >= 0){
				clearInterval(refresh);
				alert("backtest successed!");
				window.location.reload();
		    }
	        if (--exp_timer < 0) {
	            clearInterval(refresh);
	            alert("backtest Failed!");
	            window.location.reload();
	        }
	    }, 1000);
	};
	
    $('#submit_js').on('click', function () {
        $(this).oneTime('500ms', 'backtest_timer', function() {console.log("tick");}, 20);
    });
	
});
