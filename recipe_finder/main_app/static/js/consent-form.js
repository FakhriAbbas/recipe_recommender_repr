$( document ).ready(function() {

    $('input[type=radio][name=q]').change(function() {
        if (this.value == 'agree') {
            $('#proceed-btn').prop('disabled', false);
        } else {
            $('#proceed-btn').prop('disabled', true);
        }
    });
});