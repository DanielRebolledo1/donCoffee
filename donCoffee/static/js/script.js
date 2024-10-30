// some scripts

// jquery ready start
$(function() {
    //////////////////////// Prevent closing from click inside dropdown
    $(document).on('click', '.dropdown-menu', function (e) {
        e.stopPropagation();
    });

    $('.js-check :radio').on('change', function() {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $('input[name=' + check_attr_name + ']').closest('.js-check').removeClass('active');
            $(this).closest('.js-check').addClass('active');
        }
    });
    
    $('.js-check :checkbox').on('change', function() {
        if ($(this).is(':checked')) {
            $(this).closest('.js-check').addClass('active');
        } else {
            $(this).closest('.js-check').removeClass('active');
        }
    });

    //////////////////////// Bootstrap tooltip
    if ($('[data-toggle="tooltip"]').length > 0) {  
        $('[data-toggle="tooltip"]').tooltip();
    }
    
    //Function to validate the password
    $('#password, #confirm_password').on('keyup', function() {
        let password = $('#password').val();
        let confirmPassword = $('#confirm_password').val();

        if (password.length < 8) {
            $('#password').css('border-color', 'red');
            $('#password-error').text('La contraseña debe tener al menos 8 caracteres.').show();
        } else {
            $('#password').css('border-color', '');
            $('#password-error').hide();
        }

        if (password && confirmPassword && password !== confirmPassword) {
            $('#confirm_password').css('border-color', 'red');
            $('#confirm-password-error').text('Las contraseñas no coinciden.').show();
        } else {
            $('#confirm_password').css('border-color', '');
            $('#confirm-password-error').hide();
        }
    });

    let swiperCards = new Swiper('.container-categories', {
        loop: true,
        spaceBetween: 32,
        grabCurser:true,
        // If we need pagination
        pagination: {
          el: '.swiper-pagination',
          clickable:true,
          dynamicBullets:true,
        },
      
        // Navigation arrows
        navigation: {
          nextEl: '.swiper-button-next',
          prevEl: '.swiper-button-prev',
        },
    
        breakpoints:{
            600:{
                slidesPerView:2,
            },
            968:{
                slidesPerView:3,
            },
    
    
        }
    
      });   
      
});

// jquery end

setTimeout(function(){
    $('#message').fadeOut('slow')
}, 4000)

//Este codigo es para que se eliminen los mensajes de error 1 por uno
 $(document).ready(function() {
     $('#message .alert').each(function(index, element) {
         setTimeout(function() {
             $(element).fadeOut('slow');
         }, 4000 * (index + 1)); // Añadimos +1 para que el primer mensaje espere 4 segundos
     });
 });

//ESTE ES EL ANTIGUO CODIGO

// jquery ready start
// $(document).ready(function() {
// 	// jQuery code


//     /* ///////////////////////////////////////

//     THESE FOLLOWING SCRIPTS ONLY FOR BASIC USAGE, 
//     For sliders, interactions and other

//     */ ///////////////////////////////////////
    

// 	//////////////////////// Prevent closing from click inside dropdown
//     $(document).on('click', '.dropdown-menu', function (e) {
//       e.stopPropagation();
//     });


//     $('.js-check :radio').change(function () {
//         var check_attr_name = $(this).attr('name');
//         if ($(this).is(':checked')) {
//             $('input[name='+ check_attr_name +']').closest('.js-check').removeClass('active');
//             $(this).closest('.js-check').addClass('active');
//            // item.find('.radio').find('span').text('Add');

//         } else {
//             item.removeClass('active');
//             // item.find('.radio').find('span').text('Unselect');
//         }
//     });


//     $('.js-check :checkbox').change(function () {
//         var check_attr_name = $(this).attr('name');
//         if ($(this).is(':checked')) {
//             $(this).closest('.js-check').addClass('active');
//            // item.find('.radio').find('span').text('Add');
//         } else {
//             $(this).closest('.js-check').removeClass('active');
//             // item.find('.radio').find('span').text('Unselect');
//         }
//     });



// 	//////////////////////// Bootstrap tooltip
// 	if($('[data-toggle="tooltip"]').length>0) {  // check if element exists
// 		$('[data-toggle="tooltip"]').tooltip()
// 	} // end if




    
// }); 
// // jquery end
