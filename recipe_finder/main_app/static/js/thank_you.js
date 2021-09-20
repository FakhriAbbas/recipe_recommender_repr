$( document ).ready(function() {


    $('#comment-btn').click(function (event) {
        var comment_text = $("#comment-txt").val();

        $.ajax({
         type: 'POST',
         url: 'submit_comment',
         data: {
             'comment_text' : comment_text
         },
         success: function(data){
             if (data['status'] == 1){
                  $("#comment-txt").notify("Thanks for your comment", "info",
                                            {
                                                autoHide: true,
                                                autoHideDelay: 1000,
                                                hideDuration: 100,
                                            }

                );
                  $("#comment-txt").val('');
             }
         }
        });
    });
});