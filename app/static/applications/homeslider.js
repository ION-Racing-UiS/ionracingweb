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
    var dots = document.getElementsByClassName("dot");
    if (n > slides.length) {slideIndex = 1 };
    if (n < 1) {slideIndex = slides.length};
    for(i = 0; i < slides.length; i++){
        console.log(slides[i].style.display);
        slides[i].style.display = "none";
    }
    
    for(i = 0; i < dots.length; i++){
        dots[i].className = dots[i].className.replace(" active", "");
    }
    slides[slideIndex - 1].style.display = "flex";
    dots[slideIndex - 1].className += "active";
}

document.addEventListener("DOMContentLoaded", () =>{
    showslide(slideIndex);
})