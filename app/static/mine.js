
$(document).ready(function(){

	function queryBacktestReady(){
	    $.ajax({
		  url: $SCRIPT_ROOT + '/auth/qeury_backtest_result',
		  data: {},
		  async: false,
		  dataType: 'json',
		  success: function (result) {
		    ret = result.result;
		  }
		});
		alert(ret);
		return ret;
	};
	
	function startTimer(duration) {
	    var exp_timer = duration;
	    var refresh = setInterval(function () {
	    	alert("exp_timer " + exp_timer);
	    	/*
		    var ret = queryBacktestReady();
		    if (ret >= 0){
				clearInterval(refresh);
				alert("backtest successed!");
				window.location.reload();
		    }
		    */
	        if (--exp_timer < 0) {
	            clearInterval(refresh);
	            alert("backtest Failed!");
	            //window.location.reload();
	        }
	    }, 1000);
	};
    
    //submit_backtest submit_js test_js_bind
    $("#test_js_bind_form").submit(function(e){
	   		alert("hello");
	   		//e.preventDefault();
  	});
   	//$("#placebo").click(function(){
	//   	$("#test_js_bind_form").submit();
  	//});
    jQuery(function ($) {
    });
    
});
