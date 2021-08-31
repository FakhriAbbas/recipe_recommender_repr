$( document ).ready(function() {

    function show_notify_message(){
        $.notify("Before you proceed, make sure to answer all questions", "error");
    }

    $('#reflection-btn').click(function (event) {
        var q1_value = $('input[name="q1"]:checked').val();
        var q2_value = $('input[name="q2"]:checked').val();
        var q3_value = $('input[name="q3"]:checked').val();
        var q4_value = $('input[name="q4"]:checked').val();
        var q5_value = $('input[name="q5"]:checked').val();
        var q6_value = $('input[name="q6"]:checked').val();
        var q7_value = $('input[name="q7"]:checked').val();

        console.log(q1_value)
        console.log(q2_value)
        console.log(q3_value)
        console.log(q4_value)
        console.log(q5_value)
        console.log(q6_value)
        console.log(q7_value)

        if( !q1_value | !q2_value | !q3_value | !q4_value | !q5_value | !q6_value | !q7_value){
            show_notify_message();
            return;
        }
        $.LoadingOverlay("show", {
            image       : "",
            text        : "Loading..."
        });
        setTimeout(function(){
            $.LoadingOverlay("text", "Preparing results...");
        }, 2500);
        setTimeout(function(){
            $.LoadingOverlay("text", "Yep, still loading...");
        }, 7000);


        $.ajax({
         type: 'POST',
         url: 'session_reflection',
         data: {
             'q1' : q1_value,
             'q2' : q2_value,
             'q3' : q3_value,
             'q4' : q4_value,
             'q5' : q5_value,
             'q6' : q6_value,
             'q7' : q7_value
         },
         success: function(data){
             if (data['status'] == 1){
                 window.location.href = data['redirect-url']
             }else{
                 alert(data['error-msg'] + ':' + 'preference');
             }
         }
        });


    });

});