
function queryBacktestReady(){
	var ret = -1;
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

function setProgressBarValue(percent){
	$("#pbar_value").text(percent + "%");
    $('#pbar').attr('aria-valuenow', percent);
	$('#pbar').css('width', percent + '%');
}

function setTimerCounter(seconds){
	$("#timer_counter").text(seconds + "s");
}

function startTimer(duration, success_path, fail_path, min_value , max_value) {
    var exp_timer = duration * 2;
    console.log(min_value + ' ' + max_value);
    var refresh = setInterval(function () {
	    var ret = queryBacktestReady();
	    if(exp_timer % 2 == 0)
	    	setTimerCounter((parseInt(exp_timer))/2);
	    console.log("exp_timer : " + exp_timer + " : " + ret);
	    if (ret >= min_value && ret <= max_value){
			var percent = parseInt( parseFloat(ret) * 100 / max_value );
			console.log(percent);
			setProgressBarValue(percent);
	    }
	    if (ret == max_value){
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
		
function level_event_bind(set_values){
	$('input[name="level"][value="tick"]').click(function (){
		//alert("tick clicked!");
		set_input_field_value('indicators',set_values[0]);
		set_input_field_value('end_spot','32000');
		set_input_field_value('maxTTL','32000');
	});
	$('input[name="level"][value="1min"]').click(function (){
		//alert("min clicked!");
		set_input_field_value('indicators',set_values[1]);
		set_input_field_value('end_spot','270');
		set_input_field_value('maxTTL','2700');
	});
	
	//console.log($('input[name="level"][value="tick"]').attr('checked'));
	//console.log($('input[name="level"][value="1min"]').attr('checked'));
	//console.log($('#show_data_config_html h4').html());
	
	if( $('input[name="level"][value="tick"]').attr('checked') == true ){
		set_input_field_value('end_spot','32000');
		set_input_field_value('maxTTL','32000');
	}
	if( $('input[name="level"][value="1min"]').attr('checked') == true ){
		set_input_field_value('end_spot','270');
		set_input_field_value('maxTTL','2700');
	}
	if($('#show_data_config_html h4').html() == 'tick'){
		set_input_field_value('end_spot','32000');
		set_input_field_value('maxTTL','32000');
	}
	if($('#show_data_config_html h4').html() == '1min'){
		set_input_field_value('end_spot','270');
		set_input_field_value('maxTTL','2700');
	}
	
};
