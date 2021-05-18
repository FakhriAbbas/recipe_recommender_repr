$( document ).ready(function() {

    function show_notify_message(){
        $.notify("Before you proceed, make sure to answer all questions", "error");
    }

    $('#q2_o3').change(function (event) {
        var value = !$('#q2_o3').is(":checked")
        $("#q2-text").prop('disabled', value);
    });

    $('#q4_o3').change(function (event) {
        var value = !$('#q4_o3').is(":checked")
        $("#q4-text").prop('disabled', value);
    });

    $('#q2_o1').change(function (event) {
        var value_q2 = $('#q2_o1').is(":checked")
        var value_q4 = $('#q4_o1').is(":checked")
        var value = false;
        if( value_q2 == true || value_q4 == true )
            value = true;
        $("#q5-text").prop('disabled', !value);
    });

    $('#q4_o1').change(function (event) {
        var value_q2 = $('#q2_o1').is(":checked")
        var value_q4 = $('#q4_o1').is(":checked")
        var value = false;
        if( value_q2 == true || value_q4 == true )
            value = true;
        $("#q5-text").prop('disabled', !value);

    });

    $('#pre-survey-btn').click(function (event) {
        var q1 = $("input:radio[name ='q1']:checked").val();
        var q2_values = read_checkbox_values('q2');
        var q2_text = $("#q2-text").val();
        var q3 = $("input:radio[name ='q3']:checked").val();
        var q4_values = read_checkbox_values('q4');
        var q4_text = $("#q4-text").val();
        var q5 = $('#q5-text').val();
        var q6 = $('#q6-text').val();
        var q7 = $("input:radio[name ='q7']:checked").val();
        var q8 = $("input:radio[name ='q8']:checked").val();
        var q9 = $("input:radio[name ='q9']:checked").val();

        console.log(q5)

        if(VALIDATION){
            var correct = true;
            if(!q1 | !q3 | !q7 | !q6 | !q8 | !q9 |
                q2_values.length == 0 | q4_values.length == 0 |
                ( !$('#q5-text').prop('disabled') & !q5)
            )
                correct = false;
            if(correct == false){
                show_notify_message();
                return;
            }
        }
        $.ajax({
         type: 'POST',
         url: 'pre_survey',
         data: {
             'q1' : q1,
             'q2[]' : q2_values,
             'q2_text' : q2_text,
             'q3' : q3,
             'q4[]' : q4_values,
             'q4_text' : q4_text,
             'q5' : q5,
             'q6' : q6,
             'q7' : q7,
             'q8' : q8,
             'q9' : q9
         },
         success: function(data){
             if (data['status'] == 1){
                 window.location.href = data['redirect-url']
             }else{
                 alert(data['error-msg'] + ':' + 'pre_survey');
             }
         }
        });
    });

});