$(".carosel").slick({
    infinite: true,
    autoplay: true,
    autoplaySpeed: 2000,
    // this value should < total # of slides, otherwise the carousel won't slide at all
    slidesToShow: 3,
    slidesToScroll: 1,
    speed: 2000,
    autoplay: true,
    dots: true,
    arrows: true,
    prevArrow: $(".carosel-nav-left"),
    nextArrow: $(".carosel-nav-right")
  });
  