$( document ).ready(function() {

    var availableTutorials  = load_ingr();

    function load_ingr(){

    }

    $( "#autocomplete" ).autocomplete({
        source: availableTutorials,
        focus: function( event, ui ) {
                  $( "#autocomplete" ).val( ui.item.label );
                     return false;
               },
        select: function (event, ui){
            console.log(ui.item.label);
            return false;
        }

    });

    $('#preference-btn').click(function (event) {
        var q1_values = read_checkbox_values('q1');
        var q3_values = read_checkbox_values('q3');

        console.log(q1_values)
        console.log(q3_values)

        if(VALIDATION){
            // TODO
        }

        // Show full page LoadingOverlay
        $.LoadingOverlay("show");


        $.ajax({
         type: 'POST',
         url: 'preference',
         data: {
             'q1[]' : q1_values,
             'q3[]' : q3_values
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