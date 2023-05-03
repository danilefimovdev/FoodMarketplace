let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],

        componentRestrictions: {'country': ['uz']},
    })

autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value
    console.log(place.address_components);

    geocoder.geocode({'address': address}, function(results, status){

        if (status == google.maps.GeocoderStatus.OK){
            var longitude = results[0].geometry.location.lng();
            var latitude = results[0].geometry.location.lat();

            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);

            $('#id_address').val(address);
        }
    });


    for(var i=0; i<place.address_components.length; i++){
        for(var j=0; j<place.address_components[i].types.length; j++){
            // get country
            if (place.address_components[i].types[j] =='country'){
                $('#id_country').val(place.address_components[i].long_name);
            }
            // get city
            if (place.address_components[i].types[j] =='locality'){
                $('#id_city').val(place.address_components[i].long_name);
            }
            // get state
            if (place.address_components[i].types[j] =='administrative_area_level_1'){
                $('#id_state').val(place.address_components[i].long_name);
            }
            // get district
            if (place.address_components[i].types[j] =='postal_code'){
                $('#id_pin_code').val(place.address_components[i].long_name);
            }
            else{
                $('#id_pin_code').val('')
            }
        }
    }
}


$(document).ready(function(){

    // add to cart
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                if(response.status == 'login_required'){
                    Swal.fire(response.message, '', 'info').then(function(){
                        window.location = '/login';
                    })
                }else if(response.status == 'Failed'){
                    Swal.fire(response.message, '', 'error')
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);
                }
            }
        })
    })

    // decrease cart
    $('.decrease_cart').on('click', function(e){
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                if(response.status == 'login_required'){
                    Swal.fire(response.message, '', 'info').then(function(){
                        window.location = '/login';
                    })
                }else if(response.status == 'Failed'){
                    Swal.fire(response.message, '', 'error')
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);
                }
            }
        })
    })

    // place the cart item quantity on load
    $('.item_qty').each(function(){
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        $('#'+the_id).html(qty)
    })
})
