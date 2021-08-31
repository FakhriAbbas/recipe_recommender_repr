$( document ).ready(function() {

    load_countries();

    function load_countries(){
        $.ajax({
           type: 'POST',
           url: 'load_cuisine',
           data: {
           },
           success: function (data){
               if(data['status'] == 1){
                    populate_autocomplete(data['data'])
               }
           }
        });


    }

    country_list = [];
    function populate_autocomplete(data){
        $( "#autocomplete" ).autocomplete({
            source: data,
            focus: function( event, ui ) {
                      $( "#autocomplete" ).val( ui.item.label + ' (' + ui.item.count +')' );
                         return false;
                   },
            select: function (event, ui){
                $( "#autocomplete" ).val('');
                var value = ui.item.value;
                // check if country already exist
                if( country_list.find( element => element[0] == value ) )
                    return;
                country_list.push( [ui.item.value , ui.item.count] )

                $('#countries-holder').after(
                    '    <span id="country-span-'+ ui.item.value +'" class="tag label label-primary">' +
                    '    <span>' + ui.item.label + ' (' + ui.item.count + ')' + '</span>' +
                    '    <a><i id="country-' + ui.item.value + '"' +
                    '          data="' + ui.item.value + '"' +
                    'class="remove glyphicon glyphicon-remove-sign glyphicon-white"></i></a>' +
                    '    </span>'
                )



                $('i[id^="country-' + ui.item.value + '"]').on('click', function () {
                    country_value =  $(this).attr('data')
                    ele = country_list.find( element => element[0] == country_value )
                    console.log(ele)

                    var index = country_list.indexOf(ele);
                    console.log('before ' + country_list)
                    country_list.splice(index, 1);
                    console.log('after ' + country_list)

                    $('#country-span-' + country_value).remove()
                    update_counter();
                });

                update_counter();

                return false;
            }
        });
    }

    function update_counter(){
        var counter = 0;
        for (const value of country_list) {
            counter = counter + value[1];
        }
        $('#counter_span').html(counter);

        if (counter < 5000)
            $("#preference-btn").prop('disabled', true);
        else
            $("#preference-btn").prop('disabled', false);

    }

    $('#modal-button-id').click(function (event) {
    });

    $('#preference-btn').click(function (event) {
        var q3_values = read_checkbox_values('q3');
        var cuisine_list = []
        $('span[id^="country-span-"]').each(function(index){
            var value = $(this).attr('id').split('-')[2];
            cuisine_list.push(value)
        });

        if(VALIDATION){
            if( cuisine_list.length == 0 ){
                $( "#autocomplete" ).notify("Select at least one cuisine to proceed", "error",
                                            {
                                                autoHide: true,
                                                autoHideDelay: 1000,
                                                hideDuration: 100,
                                            }
                );
                return
            }
        }

        // Show full page LoadingOverlay
        // $.LoadingOverlay("show");
        $.LoadingOverlay("show", {
            image       : "",
            text        : "Loading..."
        });
        setTimeout(function(){
            $.LoadingOverlay("text", "Yep, still loading...");
        }, 2500);
        setTimeout(function(){
            $.LoadingOverlay("text", "Preparing results...");
        }, 5000);


        $.ajax({
         type: 'POST',
         url: 'preference',
         data: {
             'q1[]' : cuisine_list,
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