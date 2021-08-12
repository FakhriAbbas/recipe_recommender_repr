$( document ).ready(function() {
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();

});

var VALIDATION = 1;

function read_checkbox_values(element_id){
    var values = [];
    $('#' + element_id +' :checked').each(function() {
        values.push($(this).val());
    });
    return values
    
}

