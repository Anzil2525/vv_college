(function($){
	"use strict";

	// Mean Menu
	$('.mean-menu').meanmenu({
		meanScreenWidth: "991" 
	});

	// Mobile Menu JS
	$(".ea-sidebar-menu-area .side-sidebar-menus ul .nav-item.has-children").on("click", function(){
		$(this).toggleClass('open');
	});

	// Header Sticky
	$(window).on('scroll',function() {
		if ($(this).scrollTop() > 120){  
			$('.ea-navbar-area').addClass("is-sticky");
		}
		else{
			$('.ea-navbar-area').removeClass("is-sticky");
		}
	});

	// Others Option For Responsive JS
	$(".others-option-for-responsive .dot-menu").on("click", function(){
		$(".others-option-for-responsive .container .container").toggleClass("active");
	});

	// Feedback Slides
	var carouselEl = $('.ea-feedback-slides');
	carouselEl.owlCarousel({
		items: 1,
		loop: true,
		margin: 30,
		nav: false,
		dots: false,
		autoplay: false,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-chevron-left'></i>",
			"<i class='bx bx-chevron-right'></i>"
		]
	});
	$(".custom-owl-prev").click(function() {
        carouselEl.trigger('next.owl.carousel');
    });
    $(".custom-owl-next").click(function() {
        carouselEl.trigger('prev.owl.carousel');
	});

	// tooltip
	var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
	var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
		return new bootstrap.Tooltip(tooltipTriggerEl)
	});
	
	// Popup Image
	// $('.popup-image').magnificPopup({
	// 	type: 'image',
	// 	gallery:{
	// 		enabled:true
	// 	}
	// });

	// Gallery Popup JS
	$('.gallery-popup').each(function() {
		$(this).magnificPopup({
			delegate: '.full-screen', 
			type: 'image',
			gallery: {
			  enabled:true
			}
		});
	});

	// Popup Video
	$('.popup-video').magnificPopup({
		disableOn: 320,
		type: 'iframe',
		mainClass: 'mfp-fade',
		removalDelay: 160,
		preloader: false,
		fixedContentPos: false
	});

	// Testimonial Slides
	$('.ea-testimonial-slides.style-one').owlCarousel({
		loop: true,
		nav: false,
		margin: 30,
		dots: true,
		autoplay: false,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-chevron-left'></i>",
			"<i class='bx bx-chevron-right'></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			576: {
				items: 1
			},
			768: {
				items: 2
			},
			1200: {
				items: 2
			}
		}
	});
	$('.ea-testimonial-slides.style-two').owlCarousel({
		items: 1,
		loop: true,
		nav: false,
		dots: true,
		margin: 30,
		autoplay: false,
		animateIn: 'fadeIn',
		animateOut: 'fadeOut',
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-chevron-left'></i>",
			"<i class='bx bx-chevron-right'></i>"
		]
	});
	$('.ea-testimonial-slides.style-three').owlCarousel({
		loop: true,
		nav: false,
		dots: true,
		margin: 30,
		autoplay: true,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-chevron-left'></i>",
			"<i class='bx bx-chevron-right'></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			576: {
				items: 1
			},
			768: {
				items: 2
			},
			992: {
				items: 2
			}
		}
	});
	$('.ea-testimonial-slides.style-four').owlCarousel({
		items: 1,
		nav: true,
		loop: true,
		margin: 30,
		dots: false,
		autoplay: false,
		animateIn: 'fadeIn',
		animateOut: 'fadeOut',
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-chevron-left'></i>",
			"<i class='bx bx-chevron-right'></i>"
		]
	});
	$('.ea-testimonial-slides.style-five').owlCarousel({
		nav: true,
		margin: 30,
		loop: true,
		dots: false,
		autoplay: false,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-chevron-left'></i>",
			"<i class='bx bx-chevron-right'></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			768: {
				items: 2
			},
			992: {
				items: 2
			}
		}
	});

	// Start Logo Carousel Slider

	// SP Logo Carousel Slider
	$('.ea-logo-carousel-slider').owlCarousel({
		nav: true,
		margin: 0,
		loop: true,
		dots: false,
		autoplay: false,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-left-arrow-alt'></i>",
			"<i class='bx bx-right-arrow-alt'></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			375: {
				items: 2
			},
			768: {
				items: 4
			},
			992: {
				items: 5
			},
			1200: {
				items: 6
			}
		}
	});

	// SP Logo Carousel Slider Four
	$('.ea-logo-carousel-slider-four').owlCarousel({
		nav: false,
		margin: 0,
		loop: true,
		dots: true,
		autoplay: false,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-left-arrow-alt'></i>",
			"<i class='bx bx-right-arrow-alt'></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			375: {
				items: 2
			},
			768: {
				items: 4
			},
			992: {
				items: 5
			},
			1200: {
				items: 6
			}
		}
	});

	// SP Logo Carousel Slider Five
	$('.ea-logo-carousel-slider-five').owlCarousel({
		nav: true,
		margin: 0,
		loop: true,
		dots: false,
		autoplay: false,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-left-arrow-alt'></i>",
			"<i class='bx bx-right-arrow-alt'></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			375: {
				items: 2
			},
			768: {
				items: 4
			},
			992: {
				items: 5
			},
			1200: {
				items: 5
			}
		}
	});
	
	// SP Logo Carousel Slider Six
	$('.ea-logo-carousel-slider-six').owlCarousel({
		nav: false,
		margin: 0,
		loop: true,
		dots: true,
		autoplay: false,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-left-arrow-alt'></i>",
			"<i class='bx bx-right-arrow-alt'></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			375: {
				items: 2
			},
			768: {
				items: 4
			},
			992: {
				items: 5
			},
			1200: {
				items: 6
			}
		}
	});

	// SP Logo Carousel Slider
	$('.ea-logo-carousel-slider-seven').owlCarousel({
		nav: true,
		margin: 0,
		loop: true,
		dots: false,
		autoplay: false,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-left-arrow-alt'></i>",
			"<i class='bx bx-right-arrow-alt'></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			375: {
				items: 2
			},
			768: {
				items: 4
			},
			992: {
				items: 5
			},
			1200: {
				items: 5
			}
		}
	});

	// SP Logo Carousel Eight
	$('.ea-logo-carousel-slider-eight').owlCarousel({
		nav: true,
		margin: 0,
		loop: true,
		dots: false,
		autoplay: false,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-left-arrow-alt'></i>",
			"<i class='bx bx-right-arrow-alt'></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			375: {
				items: 2
			},
			768: {
				items: 4
			},
			992: {
				items: 5
			},
			1200: {
				items: 5
			}
		}
	});

	// SP Logo Carousel Slider Ten
	$('.ea-logo-carousel-slider-ten').owlCarousel({
		nav: true,
		margin: 0,
		loop: true,
		dots: false,
		autoplay: false,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-left-arrow-alt'></i>",
			"<i class='bx bx-right-arrow-alt'></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			375: {
				items: 2
			},
			768: {
				items: 4
			},
			992: {
				items: 5
			},
			1200: {
				items: 5
			}
		}
	});

	// Progress Bar
	//skill JS
	$('.skill-bar').each(function() {
		$(this).find('.progress-content').animate({
		width:$(this).attr('data-percentage')
		},2000);
		
		$(this).find('.progress-number-mark').animate(
		{left:$(this).attr('data-percentage')},
		{
			duration: 2000,
			step: function(now, fx) {
			var data = Math.round(now);
			$(this).find('.percent').html(data + '%');
			}
		});  
	});

	// Progress Bar JS
	$(".progress-bar").loading();

	// FAQ Accordion JS
	$('.accordion').find('.accordion-title').on('click', function(){
		// Adds Active Class
		$(this).toggleClass('active');
		// Expand or Collapse This Panel
		$(this).next().slideToggle('fast');
		// Hide The Other Panels
		$('.accordion-content').not($(this).next()).slideUp('fast');
		// Removes Active Class From Other Titles
		$('.accordion-title').not($(this)).removeClass('active');		
	});

	// Odometer JS
	$('.odometer').appear(function(e) {
		var odo = $(".odometer");
		odo.each(function() {
			var countNumber = $(this).attr("data-count");
			$(this).html(countNumber);
		});
	});

	// Search Popup JS
	$('.close-btn').on('click', function() {
		$('.search-overlay').fadeOut();
		$('.search-btn').show();
		$('.close-btn').removeClass('active');
	});
	$('.search-btn').on('click', function() {
		$(this).hide();
		$('.search-overlay').fadeIn();
		$('.close-btn').addClass('active');
	});

	// Sidebar Modal JS
	$(".burger-menu").on('click',  function() {
		$('.sidebar-modal').toggleClass('active');
	});
	$(".sidebar-modal-close-btn").on('click',  function() {
		$('.sidebar-modal').removeClass('active');
	});

	// Sidebar Menu JS
	$('#sidebar-menu-active').sidebarMenus();

	$('#sidebar-menu-active .has-children > a').on('click', function (e) {
		e.preventDefault();
	});

	$(".sidebar-menus").on("click", function (e) {
		e.preventDefault();
		$(".menu-slide-bar").toggleClass("show");
		$("body").addClass("on-side");
		$('.body-overlay').addClass('active');
		$(this).addClass('open');
	});

	$(".close-sidebar-menus > a").on("click", function (e) {
		e.preventDefault();
		$(".menu-slide-bar").removeClass("show");
		$("body").removeClass("on-side");
		$('.body-overlay').removeClass('active');
		$('.sidebar-menus').removeClass('open');
	});

	$('.body-overlay').on('click', function () {
		$(this).removeClass('active');
		$(".menu-slide-bar").removeClass("show");
		$("body").removeClass("on-side");
		$('.sidebar-menus').removeClass('open');
	});

	// SP Blog Post Slider JS
	$('.ea-blog-post-slider').owlCarousel({
		loop: true,
		nav: true,
		dots: false,
		margin: 30,
		autoplay: true,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-left-arrow-alt'></i>",
			"<i class='bx bx-right-arrow-alt'></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			576: {
				items: 1
			},
			768: {
				items: 1
			},
			992: {
				items: 1
			}
		}
	});


	// SP Review Slider JS
	$('.ea-review-slider-1').owlCarousel({
		items: 1,
		loop: true,
		nav: false,
		dots: true,
		margin: 30,
		autoplay: true,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-left-arrow-alt'></i>",
			"<i class='bx bx-right-arrow-alt'></i>"
		],
	});

	// SP Review Slider JS
	$('.ea-review-slider-2').owlCarousel({
		items: 1,
		loop: true,
		nav: true,
		dots: false,
		margin: 30,
		autoplay: true,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-chevron-left' ></i>",
			"<i class='bx bx-chevron-right' ></i>"
		],
	});


	// SP Review Slider JS
	$('.ea-review-slider-3').owlCarousel({
		items: 1,
		loop: true,
		nav: false,
		dots: false,
		margin: 30,
		autoplay: true,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-chevron-left' ></i>",
			"<i class='bx bx-chevron-right' ></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			576: {
				items: 1
			},
			768: {
				items: 2
			},
			992: {
				items: 2
			}
		}
	});

	// SP Review Slider JS
	$('.ea-review-slider-4').owlCarousel({
		items: 1,
		loop: true,
		nav: true,
		dots: false,
		margin: 30,
		autoplay: true,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-left-arrow-alt'></i>",
			"<i class='bx bx-right-arrow-alt'></i>"
		],
	});

	// SP Review Slider JS
	$('.ea-review-slider-5').owlCarousel({
		items: 1,
		loop: true,
		nav: false,
		dots: false,
		margin: 30,
		autoplay: true,
		autoplayHoverPause: true,
		navText: [
			"<i class='bx bx-left-arrow-alt'></i>",
			"<i class='bx bx-right-arrow-alt'></i>"
		],
		responsive: {
			0: {
				items: 1
			},
			576: {
				items: 1
			},
			768: {
				items: 2
			},
			992: {
				items: 3
			}
		}
	});

	// Data Aos
    AOS.init({
        once: true,
        disable: function() {
            var maxWidth = 991;
            return window.innerWidth < maxWidth;
        }
    })

}(jQuery));