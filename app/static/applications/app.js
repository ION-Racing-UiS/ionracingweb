/* global $ */
var usernames = [];
var team_id = "";
let user_name = "";
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
    var csrftoken = $('meta[name=csrf-token]').attr('content');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    });
    if (document.title === "ION Racing | Contact") {
        var compBtn = document.getElementById("comp_issue");
        var messBtn = document.getElementById("message");
        var regiBtn = document.getElementById("registration");
        compBtn.addEventListener("click", function () { formSelect(compBtn.id) });
        messBtn.addEventListener("click", function () { formSelect(messBtn.id) });
        regiBtn.addEventListener("click", function () { formSelect(regiBtn.id) });
    } else if (document.title === "ION Racing | User Reg") {
        $("#submit").addClass(" btn-primary");
    } else if (document.title === "ION Racing | Edit Report") {
        /*var csrftoken = $('meta[name=csrf-token]').attr('content');
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken)
                }
            }
        });*/
        console.log("Adding change listener")
        $("#md-form").change(function() {
            let d = document.getElementById("md-form").value;
            $.ajax({
                url: "/appuser_reportonchange",
                type: "POST",
                data: {"text": d},
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                success: function (resp) {
                    console.log("Sent Data: " + d)
                    console.log("Response: " + resp)
                    let view = document.getElementById("md-view");
                    view.innerHTML = resp;
                }
            });
        });
    } else if (document.title === "ION Racing | Delete Cars") {
        cars = document.getElementsByClassName("car");
        for (let i = 0; i < cars.length; i++) {
            let e = cars[i];
            e.addEventListener("click", function () {
                if (e.classList.contains("selected")) {
                    e.classList.remove("selected");
                    removeFromSelection(e.children[0].textContent);
                } else {
                    e.classList.add("selected");
                    addToSelection(e.children[0].textContent);
                }
            });
        }
    } else if (document.title === "ION Racing | Manage Teams") {
        $.ajax({
            url: "/query/cn/all",
            method: "POST",
            success: function(resp) {
                for (let k in resp) {
                    usernames[usernames.length] = resp[k];
                }
            }
        });
        let teams = document.getElementsByClassName("team");
        for (let i = 0; i < teams.length; i++) {
            let e = teams[i];
            e.addEventListener("click", function () {
                let team = e.textContent;
                team_id = team;
                $.ajax({
                    url: "/admin_team/" + team,
                    type: "POST",
                    success: function (resp) {
                        $("#view").empty();
                        $("#view").append(resp);
                        let a = document.getElementById("addMember");
                        a.addEventListener("click", function () {
                            let u = document.getElementById("search");
                            let r;
                            $.ajax({
                                url: "/group/add/" + team_id + "/" + u.value,
                                type: "POST",
                                success: function(resp) {
                                    if (usernames.includes(resp)) {
                                        $.ajax({
                                            url: "/admin_team/" + team_id,
                                            type: "POST",
                                            success: function(resp) {
                                                $("#view").empty();
                                                $("#view").append(resp);
                                                u.value = "";
                                            }
                                        })
                                    }
                                }
                            });
                        });
                        let r = document.getElementById("removeMembers");
                        r.addEventListener("click", function() {
                            let m = document.getElementById("selected");
                            let s = "";
                            if (m.value[m.value.length-1] === ",") {
                                s = m.value.substring(0, m.value.length-1);
                            } else {
                                s = m.value
                            }
                            let d = {"username": s};
                            $.ajax({
                                url: "/group/remove/" + team_id,
                                type: "POST",
                                data: d,
                                dataType: "json",
                                contentType: "application/json; charset=utf-8",
                                success: function(resp) {
                                    if (resp === "") {
                                        alert("Unable to remove users from the team!");
                                    } else if (resp !== "") {
                                        alert("Removed users:" + resp + " from team: " + team_id);
                                    }
                                    $.ajax({
                                        url: "/admin_team/" + team_id,
                                        type: "POST",
                                        success: function(resp) {
                                            $("#view").empty();
                                            $("#view").append(resp);
                                        }
                                    });
                                },
                                error: function(resp) {
                                    $.ajax({
                                        url: "/admin_team/" + team_id,
                                        type: "POST",
                                        success: function(resp) {
                                            $("#view").empty();
                                            $("#view").append(resp);
                                        }
                                    });
                                }
                            })
                        });                
                        let addMemberLabel = document.getElementById("addMemberLabel");
                        let removeMemberLabel = document.getElementById("removeMembersLabel");
                        let search = document.getElementById("search");
                        let addMember = document.getElementById("addMember");
                        let removeMembers = document.getElementById("removeMembers");
                        let members = document.getElementsByClassName("member");
                        for (let i = 0; i < members.length; i++) {
                            let member = members[i];
                            let selected = document.getElementById("selected");
                            member.addEventListener("click", function() {
                                if (member.classList.contains("selected")) {
                                    member.classList.remove("selected");
                                    removeFromSelection(member.children[1].textContent);
                                    if (selected.value === "") {
                                        // Restore add elements
                                        addMemberLabel.style.display = "block";
                                        removeMemberLabel.style.display = "none";
                                        removeMemberLabel.parentElement.setAttribute("colspan", "0");
                                        search.style.display = "block";
                                        search.parentElement.setAttribute("colspan", "3");
                                        addMember.style.display = "block";
                                        removeMembers.style.display = "none";
                                    }
                                } else {
                                    member.classList.add("selected");
                                    addToSelection(member.children[1].textContent)
                                    if (selected.value !== "") {
                                        // Hide add elements
                                        addMemberLabel.style.display = "none";
                                        removeMemberLabel.style.display = "block";
                                        removeMemberLabel.parentElement.setAttribute("colspan", "3");
                                        search.style.display = "none";
                                        search.parentElement.setAttribute("colspan", "0");
                                        addMember.style.display = "none";
                                        removeMembers.style.display = "block";
                                    }
                                }
                            });
                        }
                    }
                });
            });
        }
    } else if (document.title === "ION Racing | Manage Users") {
        $.ajax({
            url: "/query/cn/all",
            type: "POST",
            success: function(resp) {
                for (let k in resp) {
                    usernames[usernames.length] = resp[k];
                }
            }
        });
        $(".clickable-row").click(function() {
            window.location = $(this).data("href");
        });
        $(".toggle").click(function() {
            $.ajax({
                url: $(this).data("href"),
                type: "POST",
                success: function(resp) {
                    console.log(resp);
                }
            })
        });
    } else if (document.title === "ION Racing | Manage Groups" || document.title === "ION Racing | Manage Admins" || document.title === "ION Racing | Manage Web Admin" || (document.title.includes("ION Racing | Manage " && document.title.includes("Users")))) {
        team_id = window.location.pathname.split("/")[2].replace("%20", " ");
        $.ajax({
            url: "/query/cn/all",
            type: "POST",
            success: function(resp) {
                for (let k in resp) {
                    usernames[usernames.length] = resp[k];
                }
            }
        });
        $.ajax({
            url: "/username",
            type: "POST",
            async: true,
            success: function(resp) {
                user_name = resp;
            }
        });
        let addMemberLabel = document.getElementById("addMemberLabel");
        let removeMemberLabel = document.getElementById("removeMembersLabel");
        let search = document.getElementById("search");
        let addMember = document.getElementById("addMember");
        let removeMembers = document.getElementById("removeMembers");
        let members = document.getElementsByClassName("member");
        for (let i = 0; i < members.length; i++) {
            let member = members[i];
            let selected = document.getElementById("selected");
            member.addEventListener("click", function() {
                if (member.classList.contains("selected")) {
                    member.classList.remove("selected");
                    removeFromSelection(member.children[0].textContent);
                    if (selected.value === "") {
                        // Restore add elements
                        addMemberLabel.style.display = "block";
                        removeMemberLabel.style.display = "none";
                        removeMemberLabel.parentElement.setAttribute("colspan", "0");
                        search.style.display = "block";
                        search.parentElement.setAttribute("colspan", "3");
                        addMember.style.display = "block";
                        removeMembers.style.display = "none";
                    }
                } else {
                    member.classList.add("selected");
                    addToSelection(member.children[0].textContent)
                    if (selected.value !== "") {
                        // Hide add elements
                        addMemberLabel.style.display = "none";
                        removeMemberLabel.style.display = "block";
                        removeMemberLabel.parentElement.setAttribute("colspan", "3");
                        search.style.display = "none";
                        search.parentElement.setAttribute("colspan", "0");
                        addMember.style.display = "none";
                        removeMembers.style.display = "block";
                    }
                }
            });
        }
        addMember.addEventListener("click", function() {
            if (search.value !== "") {
                $.ajax({
                    url: "/group/add/" + team_id + "/" + search.value,
                    type: "POST",
                    success: function(resp) {
                        if (usernames.includes(resp)) {
                            search.value = "";
                        }
                    },
                    complete: function() {
                        window.location.href = window.location.pathname.replace("/" + team_id.replace(" ", "%20"), "");
                    }
                })
            }
        });
        removeMembers.addEventListener("click", function() {
            let selected = document.getElementById("selected");
            let s = "";
            if (selected.value[selected.value.length-1] === ",") {
                s = selected.value.substring(0, selected.value.length-1);
            } else {
                s = selected.value;
            }
            let c = false;
            if ($("#selected").val().includes(user_name)) {
                c = confirm("You are about to remove yourself from this group. Are you sure?");
            } else {c = true;}
            let d = {"username": s};
            if (c) {
                $.ajax({
                    url: "/group/remove/" + team_id,
                    type: "POST",
                    data: d,
                    dataType: "json",
                    contentType: "application/json; charset=utf-8",
                    success: function(resp) {
                        if (resp === "") {
                            alert("Unable to remove users from the group!");
                        } else if (resp !== "") {
                            alert("Removed users: " + resp + " from group: " + team_id);
                        }
                    },
                    complete: function() {
                        window.location.href = window.location.pathname.replace("/" + team_id.replace(" ", "%20"), "");
                    }
                })
            } else {
                for (let i = 0; i < members.length; i++) {
                    let member = members[i];
                    let selected = document.getElementById("selected");
                    if (member.classList.contains("selected")) {
                        member.classList.remove("selected");
                        removeFromSelection(member.children[0].textContent);
                        if (selected.value === "") {
                            // Restore add elements
                            addMemberLabel.style.display = "block";
                            removeMemberLabel.style.display = "none";
                            removeMemberLabel.parentElement.setAttribute("colspan", "0");
                            search.style.display = "block";
                            search.parentElement.setAttribute("colspan", "3");
                            addMember.style.display = "block";
                            removeMembers.style.display = "none";
                        }
                    } /*else {
                        member.classList.add("selected");
                        addToSelection(member.children[0].textContent)
                        if (selected.value !== "") {
                            // Hide add elements
                            addMemberLabel.style.display = "none";
                            removeMemberLabel.style.display = "block";
                            removeMemberLabel.parentElement.setAttribute("colspan", "3");
                            search.style.display = "none";
                            search.parentElement.setAttribute("colspan", "0");
                            addMember.style.display = "none";
                            removeMembers.style.display = "block";
                        }
                    } */
                }
            }
        })
        $(".member").click(function() {
            let c = $(this).children(":first-child");
        })
    } else if (document.title === "ION Racing | Manage Posts") {
        $(".clickable-row").click(function() {
            window.location = $(this).data("href");
        });
    } else if (document.title === "ION Racing | User Reg") {
        if ($("#c").val() !== "NO") {
            $("#c").val("NO");
        }
    } else if (document.title.includes("ION Racing | Manage ")) {
        let toggle = document.getElementById("toggle");
        if (toggle.value.toLowerCase() === "true") {
            $("#overlay").addClass("overlay-color");
            $("#overlay").addClass("disabled");
            toggle.textContent = "Enable";
        } else if (toggle.value.toLowerCase() === "false") {
            $("#overlay").removeClass("overlay-color");
            $("#overlay").removeClass("disabled");
            toggle.textContent = "Disable";
        }
        toggle.addEventListener("click", function() {
            let val = document.getElementById("toggle").value;
            if (document.getElementById("toggle").value.toLowerCase() === "true") {
                document.getElementById("toggle").value = "False";
                document.getElementById("toggle").textContent = "Disable";
                console.log("Toggle.value set to: " + document.getElementById("toggle").value);
                $("#overlay").removeClass("overlay-color");
                $("#overlay").removeClass("disabled");
            } else if (document.getElementById("toggle").value.toLowerCase() === "false") {
                document.getElementById("toggle").value = "True";
                document.getElementById("toggle").textContent = "Enable";
                console.log("Toggle.value set to: " + document.getElementById("toggle").value);
                $("#overlay").addClass("overlay-color");
                $("#overlay").addClass("disabled");
            }
            console.log("Toggle.value before send: " + document.getElementById("toggle").value);
            $.ajax({
                url: "/disable/" + $("#cn").val() + "/" + document.getElementById("toggle").value,
                type: "POST",
                success: function(resp) {
                    console.log("Reponse: " + resp);
                    document.getElementById("toggle").value = resp;
                }
            })
        })
    } else if (document.title === "ION Racing | Delete User(s)") {
        $.ajax({
            url: "/query/cn/all",
            type: "POST",
            success: function(resp) {
                for (let k in resp) {
                    usernames[usernames.length] = resp[k];
                }
            }
        });
        let search = document.getElementById("search");
        let removeMembers = document.getElementById("removeMembers");
        let members = document.getElementsByClassName("member");
        let selection = document.getElementById("selection");
        for (let i = 0; i < members.length; i++) {
            let member = members[i];
            let selected = document.getElementById("selected");
            member.addEventListener("click", function() {
                if (member.classList.contains("selected")) {
                    member.classList.remove("selected");
                    removeFromSelection(member.children[0].textContent);
                    for (let i = 0; i < selection.children.length; i++) {
                        if (selection.children[i].id === member.children[0].textContent) {
                            selection.children[i].remove();
                        }
                    }
                } else {
                    member.classList.add("selected");
                    addToSelection(member.children[0].textContent);
                    selection.innerHTML += "<p id=" + member.children[0].textContent + ">" + member.children[0].textContent + "</p>"
                }
            });
        }
        removeMembers.addEventListener("click", function() {
            let m = document.getElementById("selected");
            let s = "";
            if (m.value[m.value.length-1] === ",") {
                s = m.value.substring(0, m.value.length-1);
            } else {
                s = m.value
            }
            let d = {"username": s}
            $.ajax({
                url: "/admin_user/remove",
                type: "POST",
                data: d,
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                success: function(resp) {
                    console.log(resp);
                    window.location.href = resp;
                    window.location.href = "/admin_user";
                },
                error: function(resp) {
                    console.log(resp);
                    window.location.href = "/admin_user";
                }
            });
            //window.location.href = "/admin_user";
        });
    } else if (document.title === "ION Racing | Delete Post(s)") {
        let posts = document.getElementsByClassName("post");
        let selection = document.getElementById("selection");
        for (let i = 0; i < posts.length; i++) {
            let post = posts[i];
            let selected = document.getElementById("selected");
            post.addEventListener("click", function() {
                if (post.classList.contains("selected")) {
                    post.classList.remove("selected");
                    removeFromSelection(post.children[0].textContent);
                    /** Loop through selection cell and remove the id from it. */
                } else {
                    post.classList.add("selected");
                    addToSelection(post.children[0].textContent);
                    /** Add html if there is a selection cell in the table. */
                }
            })
        }
    }
    $(".flash-element").click(function(e) {
        e.preventDefault();	
        $(this).parent("li").remove();
    });
    $(".flash-element").hover(
        function(event) {
            $(this).parent("li").addClass("del");
        },
        function(event) {
            $(this).parent("li").removeClass("del");
        }
    );
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
    if ((/\s{2,}/g).test(document.getElementById("givenName").value)) {
        alert("First name" + err);
    }
    if ((/\s{2,}/g).test(document.getElementById("sn").value)) {
        alert("Last name" + err);
    }
    let fname = document.getElementById("givenName").value.replace(reg, "").replace(/\s{2,}/g, " ");
    let lname = document.getElementById("sn").value.replace(reg, "").replace(/\s{2,}/g, " ");
    let username = fname.toLowerCase().replace(" ", ".").replace("..", ".") + "." + lname.toLowerCase().replace(" ", ".").replace("..", "."); // Creates the username
    let fullname = fname + " " + lname; // Creates the full name of the user
    document.getElementById("givenName").value = fname[0].toUpperCase() + fname.substring(1, fname.length); // Capitalization check
    document.getElementById("sn").value = lname[0].toUpperCase() + lname.substring(1, lname.length); // Capitalization check
    document.getElementById("username").value = username;
    document.getElementById("username").value = document.getElementById("username").value.replace(" .", ".");
    document.getElementById("fullname").value = fullname;
}

function addToSelection(id) {
    if (document.getElementById("selected").value === ",") {
        document.getElementById("selected").value = "";
    }
    if (document.getElementById("selected").value[0] == ",") {
        let e = document.getElementById("selected");
        $("#selected").val(e.value.substring(1, e.value.length)).trigger("change");
    }
    if (!document.getElementById("selected").value.includes(id)) {
        $("#selected").val(document.getElementById("selected").value += id + ",").trigger("change");
    } else {
        console.log(id + " Already in selection!");
    }
    console.log(id + " Added to selection.");
    console.log("Selected:\t" + document.getElementById("selected").value);
}

function removeFromSelection(id) {
    $("#selected").val(document.getElementById("selected").value.replace(id, "").replace(",,", ","));
    console.log(id + " Removed from selection.");
    if (document.getElementById("selected").value === ",") {
        $("#selected").val("").trigger("change");
    }
    if (document.getElementById("selected").value[0] == ",") {
        let e = document.getElementById("selected");
        $("#selected").val(e.value.substring(1, e.value.length)).trigger("change");
    }
    console.log("Selected:\t" + document.getElementById("selected").value);
}

function autocomplete(inp, arr) {
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function(e) {
        var a, b, i, val = this.value;
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!val) { return false;}
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);
        /*for each item in the array...*/
        if (val === "*") {
            for (i = 0; i < arr.length; i++) {
                /*create a DIV element for each matching element:*/
                b = document.createElement("DIV");
                /*make the matching letters bold:*/
                b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                b.innerHTML += arr[i].substr(val.length);
                /*insert a input field that will hold the current array item's value:*/
                b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function(e) {
                /*insert the value for the autocomplete text field:*/
                inp.value = this.getElementsByTagName("input")[0].value;
                /*close the list of autocompleted values,
                (or any other open lists of autocompleted values:*/
                closeAllLists();
                if (document.title === "ION Racing | Manage Users") {
                    window.location.href = "/admin_user/user/" + inp.value;
                } else if (document.title === "ION Racing | Delete User(s)") {
                    addToSelection(inp.value);
                    document.getElementById("selection").innerHTML += "<p id=" + inp.value + ">" + inp.value + "</p>";
                    for (let i = 0; i < document.getElementsByClassName("member").length; i++) {
                        if (document.getElementsByClassName("member")[i].children[0].textContent === inp.value) {
                            document.getElementsByClassName("member")[i].classList.add("selected");
                        }
                    }
                    inp.value = "";
                }
            });
            a.appendChild(b);
            }
        } else {
            for (i = 0; i < arr.length; i++) {
                /*check if the item starts with the same letters as the text field value:*/
                if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                        /*create a DIV element for each matching element:*/
                        b = document.createElement("DIV");
                        /*make the matching letters bold:*/
                        b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                        b.innerHTML += arr[i].substr(val.length);
                        /*insert a input field that will hold the current array item's value:*/
                        b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                        /*execute a function when someone clicks on the item value (DIV element):*/
                        b.addEventListener("click", function(e) {
                        /*insert the value for the autocomplete text field:*/
                        inp.value = this.getElementsByTagName("input")[0].value;
                        /*close the list of autocompleted values,
                        (or any other open lists of autocompleted values:*/
                        closeAllLists();
                        if (document.title === "ION Racing | Manage Users") {
                            window.location.href = "/admin_user/user/" + inp.value;
                        } else if (document.title === "ION Racing | Delete User(s)") {
                            if (!document.getElementById("selected").value.includes(inp.value)) {
                                addToSelection(inp.value);
                                document.getElementById("selection").innerHTML += "<p id=" + inp.value + ">" + inp.value + "</p>";
                            }
                            for (let i = 0; i < document.getElementsByClassName("member").length; i++) {
                                if (document.getElementsByClassName("member")[i].children[0].textContent === inp.value) {
                                    document.getElementsByClassName("member")[i].classList.add("selected");
                                }
                            }
                            inp.value = "";
                        }
                    });
                    a.appendChild(b);
                }
            }
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 38) { //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
                /*and simulate a click on the "active" item:*/
                if (x) x[currentFocus].click();
            }
        }
    });
    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }
    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
            x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
} 
