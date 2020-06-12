$(function () {
        $(document).scroll(function () {
          var $nav = $(".nav-wrapper");
          $nav.toggleClass("scrolled", $(this).scrollTop() > $nav.height());
        });
      });