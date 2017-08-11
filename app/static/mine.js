
function queryBacktestReady(){
	var stp = -1;
	var status = -1;
    $.ajax({
	  url: $SCRIPT_ROOT + '/auth/query_backtest_result',
	  data: {},
	  async: false,
	  dataType: 'json',
	  success: function (result) {
	    step = result.step;
	    status = result.status;
	  }
	});
	var retArray = new Array(2);
	retArray[0] = step;
	retArray[1] = status;
	return retArray;
};

function setProgressBarValue(percent){
	$("#pbar_value").text(percent + "%");
    $('#pbar').attr('aria-valuenow', percent);
	$('#pbar').css('width', percent + '%');
}

function setTimerCounter(seconds){
	$("#timer_counter").text(seconds + "s");
}

function startTimer(duration, success_path, fail_path, min_value , max_value) {
    var exp_timer = duration;
    console.log(min_value + ' ' + max_value);
    var refresh = setInterval(function () {
    	var ret = [0,0];
    	//wait for two seconds, then query in order to avoid network laging
    	if( exp_timer + 1 < duration)
	    	ret = queryBacktestReady();
	    var step = parseInt(ret[0]);
	    var status = parseInt(ret[1]);
	    setTimerCounter((parseInt(exp_timer)));
	    console.log("exp_timer : " + exp_timer + " : " + step);
	    if (step >= min_value && step <= max_value){
			var percent = parseInt( parseFloat(step) * 100 / max_value );
			console.log(percent);
			setProgressBarValue(percent);
	    }
	    if (step == max_value){
			clearInterval(refresh);
			console.log("backtest successed!");
			window.location.href = success_path;
	    }
        if (--exp_timer < 0 || status < 0 ) {
            clearInterval(refresh);
            console.log("backtest Failed!");
            if(exp_timer < 0)
            	window.location.href = fail_path + "?error_code=" + 100;
            else
            	window.location.href = fail_path + "?error_code=" + step;
        }
    }, 1000);
};
	
var entry_rule_table = $('#entry_rule_table'),
	entry_rule_submit_button = $('#entry_rule_submit_button'),
	entry_rule_remove_row_button = $('#entry_rule_remove_row_button'),
	entry_rule_clear_all_button = $('#entry_rule_clearAll');
    	
function submit_table(to_be_submitted,tar_url){
	var data = to_be_submitted.bootstrapTable('getData');
	var json_data = JSON.stringify( data );
	console.log('submit data');
	for(i=0;i<data.length;i++)
		console.log(JSON.stringify( data[i] ));
  	$.ajax({
  		type:"POST",
        url: tar_url,
        data: { data : json_data },
        dataType: "json",
       	async: true,
        success: function (data, status) {
            if (status == "success") {
                console.log("Success");
            }
        },
        error: function () {
            console.log("error");
        },
        complete: function () {
        }
	});                        	
};	

entry_rule_submit_button.click(function () {
	 console.log('click exit submit button');
     var tar_table = entry_rule_table;
     var url = $SCRIPT_ROOT + '/auth/update_entry_rule_data';
     submit_table(tar_table,url);
});     

entry_rule_remove_row_button.click(function () {
    var ids = $.map(entry_rule_table.bootstrapTable('getSelections'), function (json_data) {
        return json_data.id;
    });
    console.log('remove exit row ' + ids);
    entry_rule_table.bootstrapTable('remove', {
        field: 'id',
        values: ids
    });
    entry_rule_submit_button.click();
}); 

entry_rule_clear_all_button.click(function () {
	console.log('remove exit all');
    entry_rule_table.bootstrapTable('removeAll');
    entry_rule_submit_button.click();
});

var exit_rule_table = $('#exit_rule_table'),
	exit_rule_submit_button = $('#exit_rule_submit_button'),
	exit_rule_remove_row_button = $('#exit_rule_remove_row_button'),
	exit_rule_clear_all_button = $('#exit_rule_clearAll');
	
exit_rule_submit_button.click(function () {
	 console.log('click exit submit button');
     var tar_table = exit_rule_table;
     var url = $SCRIPT_ROOT + '/auth/update_exit_rule_data';
     submit_table(tar_table,url);
});     

exit_rule_remove_row_button.click(function () {
    var ids = $.map(exit_rule_table.bootstrapTable('getSelections'), function (json_data) {
        return json_data.id;
    });
    console.log('remove exit row ' + ids);
    exit_rule_table.bootstrapTable('remove', {
        field: 'id',
        values: ids
    });
    exit_rule_submit_button.click();
}); 

exit_rule_clear_all_button.click(function () {
	console.log('remove exit all');
    exit_rule_table.bootstrapTable('removeAll');
    exit_rule_submit_button.click();
});

//for radio button checked
function set_input_selected_checked(nameStr, type, value){
	var selector = "input[name="+nameStr+"]";
	if(type != null) {
		if(type == "radio" || type == "checkbox"){
			var obj = $(selector);
			for(var i=0; i<obj.length;i++)
				if(obj[i].value == value)
					obj[i].checked = "checked";
		}
	}
	else{
		$(selector).val(value);
	}
}

function set_radio_selected_checked(name, selectdValue) {
    $('input[name="' + name+ '"][value="' + selectdValue + '"]').prop('checked', true);
};

function set_input_field_value(name,value) {
	var selector = "input[name="+name+"]";
	$(selector).val(value);
};
				
function level_event_bind(mode,show_indicator_values){

	var spots_perday_tick = new Array(5);
	spots_perday_tick[0] = 32402;
	spots_perday_tick[1] = 27002;
	spots_perday_tick[2] = 28802;
	var spots_perday_1min = new Array(5);
	spots_perday_1min[0] = 270;
	spots_perday_1min[1] = 225;
	spots_perday_1min[2] = 240;
	var spots_perday_day = new Array(5);
	spots_perday_day[0] = 1;
	spots_perday_day[1] = 1;
	spots_perday_day[2] = 1;
	
	//var multi_selected = $('#instruments');
	//console.log(multi_selected.html());
	
	//alert($('input[name="level"][value="day"]').attr('checked'));
	
	//console.log(show_indicator_values);
	$('input[name="level"][value="tick"]').click(function (){
		//alert("tick clicked!");
		set_input_field_value('indicators',show_indicator_values[mode][0]);
		set_input_field_value('end_spot',spots_perday_tick[mode]);
		set_input_field_value('maxTTL',spots_perday_tick[mode]);
	});
	$('input[name="level"][value="1min"]').click(function (){
		//alert("min clicked!");
		set_input_field_value('indicators',show_indicator_values[mode][1]);
		set_input_field_value('end_spot',spots_perday_1min[mode]);
		set_input_field_value('maxTTL',spots_perday_1min[mode] * 10);
	});
	$('input[name="level"][value="day"]').click(function (){
		//alert("min clicked!");
		set_input_field_value('indicators',show_indicator_values[mode][1]);
		set_input_field_value('end_spot',spots_perday_day[mode]);
		set_input_field_value('maxTTL',spots_perday_day[mode] * 256);
	});
	
	//console.log($('input[name="level"][value="tick"]').attr('checked'));
	//console.log($('input[name="level"][value="1min"]').attr('checked'));
	//console.log($('#show_data_config_html h4').html());
	
	//has not been submitted to server, but checkbox value changed,as data comes from server, so this is essential
	if( $('input[name="level"][value="tick"]').attr('checked') == "checked" ){
		set_input_field_value('indicators',show_indicator_values[mode][0]);
		set_input_field_value('end_spot',spots_perday_tick[mode]);
		set_input_field_value('maxTTL',spots_perday_tick[mode]);
	}
	if( $('input[name="level"][value="1min"]').attr('checked') == "checked" ){
		set_input_field_value('indicators',show_indicator_values[mode][1]);
		set_input_field_value('end_spot',spots_perday_1min[mode]);
		set_input_field_value('maxTTL',spots_perday_1min[mode] * 10);
	}
	if( $('input[name="level"][value="day"]').attr('checked') == "checked" ){
		//alert("min clicked 2!");
		set_input_field_value('indicators',show_indicator_values[mode][1]);
		set_input_field_value('end_spot',spots_perday_day[mode]);
		set_input_field_value('maxTTL',spots_perday_day[mode] * 256);
	}
	
	//already submitted to server
	if($('#show_data_config_html h4').html() == 'tick'){
		set_input_field_value('indicators',show_indicator_values[mode][0]);
		set_input_field_value('end_spot',spots_perday_tick[mode]);
		set_input_field_value('maxTTL',spots_perday_tick[mode]);
	}
	if($('#show_data_config_html h4').html() == '1min'){
		set_input_field_value('indicators',show_indicator_values[mode][1]);
		set_input_field_value('end_spot',spots_perday_1min[mode]);
		set_input_field_value('maxTTL',spots_perday_1min[mode] * 10);
	}
	if($('#show_data_config_html h4').html() == 'day'){
		//alert("min clicked 3!");
		set_input_field_value('indicators',show_indicator_values[mode][1]);
		set_input_field_value('end_spot',spots_perday_day[mode]);
		set_input_field_value('maxTTL',spots_perday_day[mode] * 256);
	}
	
};
