
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
	return ret;
};

function startTimer(duration, success_path, fail_path) {
    var exp_timer = duration * 2;
    var refresh = setInterval(function () {
	    var ret = queryBacktestReady();
	    console.log("exp_timer : " + exp_timer + " : " + ret);
	    if (ret >= 0){
			clearInterval(refresh);
			console.log("backtest successed!");
			window.location.href = success_path;
	    }
        if (--exp_timer < 0) {
            clearInterval(refresh);
            console.log("backtest Failed!");
            window.location.href = fail_path;
        }
    }, 500);
};

//submit_backtest submit_js test_js_bind
//$("#test_js_bind_form").submit(function(e){
//   		alert("hello");
   		//e.preventDefault();
//});

//$("#placebo").click(function(){
//   	$("#test_js_bind_form").submit();
//});

//jQuery(function ($) {
//});

