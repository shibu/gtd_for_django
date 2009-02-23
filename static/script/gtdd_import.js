// Start Up
$(document).ready(function() {
    $('#login_messagebox').fadeIn("slow").pause(2000).fadeOut("slow");
    $("input[name='mode']").change(function() {
        $.post(location.href,
               {method:"export", mode:$("input[name='mode']:checked").val()},
               function(return_value, status) {
                   $('#import_data').val(return_value);
               },
               "text");
    });

    $('#import_form').submit(function() {
        task = $('#task_input');
        if (task.val() === "") {
          return false;
        }
        $.post(location.href,
               {
                   method:"import",
                   mode:$("input[name='mode']:checked").val(),
                   import_data:$('#import_data').val()
               },
               function(return_value, status) {
                   $('#message_area').text(return_value);
                   var message_box = $('#message_box');
                   message_box
                       .fadeIn('slow')
                       .pause(2000)
                       .fadeOut('slow', function() {
                           message_box.text("");
                       });
               },
               "text");
        $('#task_table').flexReload();

        return false;
    });
});