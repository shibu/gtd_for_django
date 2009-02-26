
$.fn.rotateClass = function() {
    var states = arguments;
    return this.each(function() {
        var next_index = -1;
        var has_null = false;
        this_elem = $(this);
        for (var i=0;i<states.length;++i) {
            state = states[i];
            if (state == null) {
                has_null = true;
            } else if (this_elem.hasClass(state)) {
                next_index = (i + 1) % states.length;
                this_elem.removeClass(state);
            }
        }
        if (next_index == -1) {
            if (has_null == true) {
                next_index = 1;
            } else {
                next_index = 0;
            }
        }
        next_class = states[next_index];
        if (next_class != null) {
            this_elem.addClass(next_class);
        }
    });
};

var set_message = function(text) {
$('#message_area').text(text);
    var message_box = $('#message_box');
    message_box
        .fadeIn('slow')
        .pause(2000)
        .fadeOut('slow');
};


// Start Up
$(document).ready(function() {
    $('#login_messagebox').fadeIn("slow").pause(2000).fadeOut("slow");

    $('#task_regist_form').submit(function() {
        task = $('#task_input');
        if (task.val() === "") {
          return false;
        }
        $.post(location.href,
               {method:"regist_task", new_task:task.val()},
               function(return_value, status) {
                   task.val("");
                   set_message(return_value);
               },
               "text");
        $('#task_table').flexReload();

        return false;
    });
    buttons = [
            {name: 'Delete', bclass: 'delete', onpress : run_command},
            {separator: true}];
    if (options.do_today) {
        buttons.push({name: 'Today', bclass: 'do_today', onpress : run_command});
    }
    if (options.defer_tomorrow) {
        buttons.push({name: 'Tomorrow', bclass: 'deferment', onpress : run_command});
    }
    if (options.defer_next_week) {
        buttons.push({name: 'Next Week', bclass: 'deferment', onpress : run_command});
    }
    if (options.change_to_memo) {
        buttons.push({name: 'Memo', bclass: 'to_memo', onpress : run_command});
    }
    if (options.do_someday) {
        buttons.push({name: 'Someday', bclass: 'do_someday', onpress : run_command});
    }
    url = location.href;
    while (url[url.length-1] == "#") {
       url = url.substring(0, url.length-1);
    }
    $('#task_table').flexigrid({
        url: url + '_table/',
        height: 'auto',
        dataType: 'json',
        sortname: 'date',
        sortorder: 'asc',
        usepager: true,
        rp: 10,
        pagestat: '{from}-{to} / Total:{total}',
        colModel : [
            {display: '', name : 'check', width : 16, sortable : true, align: 'left'},
            {display: '', name : 'icon', width : 16, sortable : true, align: 'left'},
            {display: 'Date', name : 'date', width : 64, sortable : true, align: 'left'},
            {display: 'Title', name : 'title', width : 305, sortable : true, align: 'left'}
            ],
        buttons : buttons,
        onSuccess : function() {
            $('.unfinished').parent().parent().parent().addClass("urow");
            $('img.check_box').click(toggle_checkbox);
            $('.text_tag').click(show_tag_dialog);
            $('.img_tag').click(show_tag_dialog);
            $('#task_input').focus();
            $('span.date').click(show_date_dialog);
        }
    });
    $('#datepicker').datepicker({
        inline: true,
        changeMonth: true,
        changeYear: true,
        onSelect: function(date) {
            $('#task_table').flexOptions({query:date, qtype:"date"});
            $('#task_table').flexReload();
        }
    });
});


var toggle_checkbox = function() {
    var current = $(this);
    var tr = current.parent().parent().parent();
    current.rotateClass(null, 'doing', 'checked');
    $.post(location.href,
           { method:"check",
             id:tr.attr('id'),
             is_check:current.hasClass('checked'),
             is_doing:current.hasClass('doing')},
           function(return_value, status) {
           },
           "text");
    tr.addClass("trSelected");
};


var show_date_dialog = function() {
    var current = $(this);
    var tr = current.parent().parent().parent();
    tr.addClass("trSelected");

    url = location.href;
    while (url[url.length-1] == "#") {
       url = url.substring(0, url.length-1);
    }

    $.post(url + '_datetime/',
           { method:"get",
             id:tr.attr('id'),
           },
           function(return_value, status) {
               init_datetime_dialog(return_value);
           },
           "json");
};

var init_datetime_dialog = function(date_values) {
    keys = ["target_date_flag", "target_date", "target_time",
            "start_date_flag", "start_date", "start_time",
            "finished_date_flag", "finished_date", "finished_time"];
    for (var i in keys) {
        var key = keys[i];
        if (date_values[key]) {
            $('#' + key).val(date_values[key]);
        } else {
            $('#' + key).val("");
        }
    }
    var dialog = $('#datetime-dialog').clone();
    $('.fg-button', dialog).hover(
        function(){
            $(this).addClass("ui-state-hover");
	    },
        function(){
            $(this).removeClass("ui-state-hover");
        }
    );
    dialog.dialog({
        modal:true,
        bgiframe: false,
        buttons: {
            'Apply': function() {
                $(this).dialog('close');
            },
            'Cancel': function() {
                $(this).dialog('close');
            }
        },
        open: function(event, ui) {
            $('.date_picker', dialog).datepicker({dateFormat: "yyyy/mm/dd"});
            $('#ui-datepicker-div').css("z-index", 1050);
        }
    })
}

var send_datetime_dialog_result = function(dialog) {
}

var show_tag_dialog = function() {
    var tag_dialog = $('<div id="tag_dialog"><table id="tag_table" style="display:none;"></div>');
    tag_dialog.attr("title", "Tag: " + $(this).attr("tag_name"));
    $('#tag_table', tag_dialog).flexigrid({
        url: '/gtd/_tag_table/',
        height: "auto",
        dataType: 'json',
        sortname: 'date',
        sortorder: 'asc',
        usepager: true,
        qtype: "tag",
        query: $(this).attr("tag_id"),
        rp: 15,
        pagestat: '{from}-{to} / Total:{total}',
        colModel : [
            {display: '', name : 'check', width : 16, sortable : true, align: 'left'},
            {display: '', name : 'icon', width : 16, sortable : true, align: 'left'},
            {display: 'Date', name : 'date', width : 64, sortable : true, align: 'left'},
            {display: 'Title', name : 'title', width : 305, sortable : true, align: 'left'}
            ],
        buttons : [
            {name: 'Delete', bclass: 'delete', onpress : run_command},
            {separator: true},
            {name: 'Today', bclass: 'do_today', onpress : run_command},
            {name: 'Memo', bclass: 'to_memo', onpress : run_command},
            {name: 'Someday', bclass: 'do_someday', onpress : run_command}
            ],
        onSuccess : function() {
            $('img.check_box').click(toggle_checkbox);
        }
    });
    tag_dialog.dialog();
};


var run_command = function(command, grid) {
    var items = $('.trSelected',grid);
    var itemlist = [];
   	for(i=0;i<items.length;i++){
        itemlist.push(items[i].id);
    }
    if (command == "Delete" || command == "Memo" || command == "Today" || command == "Someday" || command == "Tomorrow" || command == "Next Week") {
        items.fadeOut("slow");
        $.post(location.href,
               { method:"edit",
                 command:command,
                 target_items:itemlist.join(",")},
               function(return_value, status) {
                   if (return_value != "No Target") {
                       $('#task_table').flexReload();
                   }
               },
               "text");
    } else {
        alert(command);
    }
};
