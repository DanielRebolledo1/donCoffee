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
