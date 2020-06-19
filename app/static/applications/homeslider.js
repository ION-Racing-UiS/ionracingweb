console.log("script loaded");
var slideIndex = 1;

function slidechange(n) {
    showslide(slideIndex += n);
}
function currentSlide(n) {
    showslide(slideIndex = n);
}

function showslide(n) {
    var i;
    var slides = document.getElementsByClassName("carslides");
    // var dots = document.getElementsByClassName("dot");
    if (n > slides.length) {slideIndex = 1 };
    if (n < 1) {slideIndex = slides.length};
    for(i = 0; i < slides.length; i++){
        console.log(slides[i].style.display);
        slides[i].style.display = "none";
    }
    // for(i = 0; i < dots.length; i++){
    //     dots[i].className = dots[i].className.replace(" active", "");
    // }
    slides[slideIndex - 1].style.display = "flex";
    // dots[slideIndex - 1].className += "active";
}
var ele_rect;
document.addEventListener("DOMContentLoaded", () =>{
    showslide(slideIndex);
    var ele = $(".carContainer")[0];
    ele_rect = ele.getBoundingClientRect();
    var interval = 500;
    var i;

    // $(document).mousemove(function(e){
    //     if (e.pageX > ele_rect.x && e.pageX < (ele_rect.right - (ele_rect.x / ele_rect.left)) 
    //         && e.pageY > ele_rect.y && e.pageY < ele_rect.bottom) {
            
    //         if (e.pageX > ele_rect.right - ele_rect.width / 4) {
    //             ele.style.background = "blue";
    //             i = setInterval(function () {
    //                 slidechange(1);
    //             }, interval);
                
    //         } else if (e.pageX < ele_rect.x + ele_rect.width / 4) {
    //             ele.style.background = "red";
    //             i = setInterval(function () {
    //                 slidechange(-1);
    //             }, interval);
    //         }
    //         clearInterval(i);
    //     }
    //     else{
    //         ele.style.background = "#011321";
    //     }
    // });
})