$('#myCollapse').on('show.bs.collapse', function () {
    $(".navbar .navbar-header .navbar-toggle").children(".icon-bar.ib1").addClass("rotateib1");
    $(".navbar .navbar-header .navbar-toggle").children(".icon-bar.ib2").addClass("rotateib2");
});

$('#myCollapse').on('hide.bs.collapse', function () {
    $(".navbar .navbar-header .navbar-toggle").children(".icon-bar.ib1").removeClass("rotateib1");
    $(".navbar .navbar-header .navbar-toggle").children(".icon-bar.ib2").removeClass("rotateib2");
});
