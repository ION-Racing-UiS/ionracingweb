console.log("script loaded");
console.log(all_cars);

var ion_cars = []
var ion_car_index = {}

var slideIndex = 1;
var last_scroll_index = 0;

function slidechange(n) {
    showslide(slideIndex += n);
}
function currentSlide(n) {
    showslide(slideIndex = n);
}
function showslide(n) {
    var i;
    var engine = document.getElementById("engine");
    var speed = document.getElementById("speed");
    var weight = document.getElementById("weight");
    var year = document.getElementById("year");
    var km_h = '<sup class="supp">km/h</sup>'
    var kg = '<sup class="supp">kg</sup>'

    var slides = document.getElementsByClassName("carslides");
    // var dots = document.getElementsByClassName("dot");
    if (n > slides.length) {slideIndex = 1 };
    if (n < 1) {slideIndex = slides.length};
    for(i = 0; i < slides.length; i++){
        slides[i].style.display = "none";
    }

    // for(i = 0; i < dots.length; i++){
    //     dots[i].className = dots[i].className.replace(" active", "");
    // }
    slides[slideIndex - 1].style.display = "flex";

    engine.innerText = ion_cars[slideIndex - 1][1]["engine"];
    
    speed.innerHTML = ion_cars[slideIndex - 1][1]["speed"] + ' ' + km_h;
    
    weight.innerHTML = ion_cars[slideIndex - 1][1]["weight"] + ' ' + kg;
    
    year.innerText = ion_cars[slideIndex - 1][1]["year"];



    // dots[slideIndex - 1].className += "active";
}

function order_car_dict() {
    for (var key in all_cars) {
        ion_cars.push([key, all_cars[key]]);
    }
    ion_cars.sort( function(a, b) {
        return (a[0] > b[0] ? -1 : 1);
    })
    for (let i = 0; i < ion_cars.length; i++) {
        const ele = ion_cars[i];

        if (!(ele[0] in ion_car_index)) {
            ion_car_index[ele[0]] = i;
        }
    }
}

function CreateMenuAndSlider() {
    let listContainer = document.getElementsByClassName("carnamelistcontainer")[0];
    let slidecontainer = document.getElementsByClassName("slidecontainer")[0];
    let li;
    let h1;
    let span_name;
    let span_numb;
    let carslides;
    let img;

    ion_cars.forEach(ele => {
        li = document.createElement("li");
        li.classList.add("carnamelist");
        h1 = document.createElement("h1");
        span_name = document.createElement("span");
        span_name.innerHTML = ele[1]["name"];
        span_name.classList.add("coolfont")
        span_name.classList.add("carname")
        
        span_numb = document.createElement("span");
        span_numb.innerHTML = ele[1]["number"];
        span_numb.classList.add("coolfont")
        span_numb.classList.add("carnumber")

        carslides = document.createElement("div");
        carslides.classList.add("carslides")
        img = document.createElement("img")
        img.classList.add("carimg")
        img.src = "/static/images/" + ele[1]["img"]


        carslides.appendChild(img)
        slidecontainer.appendChild(carslides)

        h1.appendChild(span_name)
        h1.appendChild(span_numb)
        li.appendChild(h1);
        listContainer.appendChild(li)

    });
}

function update_active_car_menu(index) {
    let listContainer = document.getElementsByClassName("carnamelistcontainer")[0];
    listContainer.children[last_scroll_index].classList.remove("carnamelistactive");
    listContainer.children[index].classList.add("carnamelistactive");
    last_scroll_index = index;
}

function check_wheel_Scroll_and_animate(event) {
    // event.preventDefault();
    console.log(event)
    if (!checkwheelscrollIsUp(event)) {
        if (last_scroll_index !== ion_cars.length - 1){
            update_active_car_menu(last_scroll_index + 1)
            slidechange(1)
        }
    }else{
        if (last_scroll_index !== 0){
            update_active_car_menu(last_scroll_index - 1)
            slidechange(-1)
        }
    }
}
  
function checkwheelscrollIsUp(event) {
    if (event.wheelDelta) {
        // console.log(event.wheelDelta > 0);
        return event.wheelDelta > 0;
    }
    // console.log(event.deltaY < 0);
    return event.deltaY < 0;
}

function disable_scroll_and_wheel_scroll(event) {
    console.log(event);
    
    event.preventDefault();
    event.stopPropagation();
    console.log(event.deltaY < 0);

    return false;
    
}
function throttle(cb, timeout) {
    // You can rewrite this function by replacing the time limit with the
    // scroll pitch. I think that would be the best solution.
    // let delta = e.deltaY || e.detail || e.wheelDelta;
    // ... sum delta and call callback by the number of steps: accumulator/step
  
    let lastCall = 0;
  
    return function() {
      if (new Date() - lastCall > timeout) {
        lastCall = new Date();
  
        cb(event);
      }
    }
}
function scrollParentToChild(parent, child) {

    // Where is the parent on page
    var parentRect = parent.getBoundingClientRect();
    // What can you see?
    var parentViewableArea = {
      height: parent.clientHeight,
      width: parent.clientWidth
    };
  
    // Where is the child
    var childRect = child.getBoundingClientRect();
    // Is the child viewable?
    var isViewable = (childRect.top >= parentRect.top) && (childRect.top <= parentRect.top + parentViewableArea.height);
  
    // if you can't see the child try to scroll parent
    if (!isViewable) {
      // scroll by offset relative to parent
      parent.scrollTop = (childRect.top + parent.scrollTop) - parentRect.top
    }
  
  
}

// function check_scroll(event) {
//     var previousScroll = 0;

// $(window).scroll(function(){
// var currentScroll = $(this).scrollTop();
// if (currentScroll > previousScroll){
//     alert('down');
// } else {
//     alert('up');
// }
// previousScroll = currentScroll;
// });
// }

function addevents() {
    let listContainer = document.getElementsByClassName("carnamelistcontainer")[0];
    listContainer.addEventListener("wheel", throttle(check_wheel_Scroll_and_animate, 250), false);
    // listContainer.removeEventListener("scroll", disable_scroll_and_wheel_scroll)

    listContainer.addEventListener("mouseenter", function(){
        console.log("her01");
        window.addEventListener("DOMMousescroll", function(e){
            e.preventDefault();
            console.log("her1");
            
            e.returnValue = false;
        }, false)
    });
    listContainer.addEventListener("mouseleave", function(){
        console.log("her02");
        window.removeEventListener("DOMMousescroll", function(e){
            e.preventDefault();
            console.log("her2");
            e.returnValue = false;
        }, false)
    });
}

document.addEventListener("DOMContentLoaded", () =>{
    order_car_dict();
    CreateMenuAndSlider();
    update_active_car_menu(0);
    addevents();
    showslide(slideIndex);
})