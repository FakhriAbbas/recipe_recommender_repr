$( document ).ready(function() {


    $('#feedback-btn').click(function (event) {
        var comment_text = $("#comment-txt").val();

        if(!comment_text){
            $.notify("Make sure to answer the question in text area", "error");
            return
        }

        if( confirm('This is your last chance to download the recipes you have added to your mealplan. Do you want to proceed?') ){
            $.ajax({
                 type: 'POST',
                 url: 'open_ended_feedback',
                 data: {
                     'comment_text' : comment_text
                 },
                 success: function(data){
                     if (data['status'] == 1){
                        window.location.href = data['redirect-url']
                     }
                 }
                });
        }else{

        }


    });
});