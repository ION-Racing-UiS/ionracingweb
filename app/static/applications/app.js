/* global $ */
// Init function
$(document).ready(function () {
    var resizeBg = function () {
        if (window.matchMedia('(min-width: 768px)').matches) {
            var remHeight = $(window).height() - $('#headarea').height();
            //$('.heading').css("padding-top", parseInt($('.heading').css("padding-top"), 10) + remHeight);
        } else {
            //$('.heading').css("padding-top", "1em");
        }
    };
    resizeBg();
    if (document.title === "ION Racing | Contact") {
        var compBtn = document.getElementById("comp_issue");
        var messBtn = document.getElementById("message");
        var regiBtn = document.getElementById("registration");
        compBtn.addEventListener("click", function () { formSelect(compBtn.id) });
        messBtn.addEventListener("click", function () { formSelect(messBtn.id) });
        regiBtn.addEventListener("click", function () { formSelect(regiBtn.id) });
    } else if (document.title === "ION Racing | User Reg") {
        $("#submit").addClass(" btn-primary");
    }
    $(window).resize(function () { resizeBg(); });
});

// Easter egg
var ion_keys = [73, 79, 78];
var ion_index = 0;
$(document).keydown(function (e) {
    //console.log(e.keyCode);
    if (e.keyCode === ion_keys[ion_index++]) {
        if (ion_index === ion_keys.length) {
            $('#headarea').css('background-image', 'linear-gradient(rgba(0, 0, 0, 0), rgba(0, 0, 0, 1)), url(/static/images/ION_CODE.png)');
        }
    } else {
        ion_index = 0;
    }
})

// Handles form buttons and returns the form with an AJAX request
function formSelect(e) {
    /**
     * Setup and send form AJAX request.
     * 
     * Uses the parameter to request a form with AJAX from the backend.
     * 
     * @alias   formSelect
     * 
     * @param   {String}    e   What contact form to request with AJAX.
     * 
     * @return  {void}  Void.
     */
    var csrftoken = $('meta[name=csrf-token]').attr('content');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    });
    $.ajax({
        url: "/contact/" + e,
        type: "POST",
        success: function (resp) {
            $("#ajaxNode").empty();
            $("#ajaxNode").append(resp);
        }
    });
}

// Sets the username for a new users
function setUsername() {
    let err = " cannot contain two or more sequential spaces.";
    let reg = /[^\u0041-\u005A\u0061-\u007A\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u024F\u1E00-\u1EFF ]/g;
    if ((/\s{2,}/g).test(document.getElementById("fname").value)) {
        alert("First name" + err);
    }
    if ((/\s{2,}/g).test(document.getElementById("lname").value)) {
        alert("Last name" + err);
    }
    let fname = document.getElementById("fname").value.replace(reg, "").replace(/\s{2,}/g, " ");
    let lname = document.getElementById("lname").value.replace(reg, "").replace(/\s{2,}/g, " ");
    let username = fname.toLowerCase().replace(" ", ".").replace("..", ".") + "." + lname.toLowerCase().replace(" ", ".").replace("..", "."); // Creates the username
    let fullname = fname + " " + lname; // Creates the full name of the user
    document.getElementById("fname").value = fname[0].toUpperCase() + fname.substring(1, fname.length); // Capitalization check
    document.getElementById("lname").value = lname[0].toUpperCase() + lname.substring(1, lname.length); // Capitalization check
    document.getElementById("username").value = username;
    document.getElementById("username").value = document.getElementById("username").value.replace(" .", ".");
    document.getElementById("fullname").value = fullname;
}