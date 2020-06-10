class CountDown {
    constructor(element, endDate, title) {
        this.mk = new HtmlHelper();
        // this.endDate = ;
        this.endDate = endDate;
        this.element = element;
        this.secSpan = this.mk.tag("div", "secs");
        this.hourSpan = this.mk.tag("div", "time");
        this.timeLeft = this.mk.tag("div", "time");
        this.element.appendChild(this.mk.tag("h1", "", null, "Time to " + title));
        this.element.appendChild(this.mk.tag("div", "", null, "Time left until: " + this.endDate.toLocaleString("nb-NO")));
        this.element.appendChild(this.hourSpan);
        this.element.appendChild(this.secSpan);
        this.element.appendChild(this.mk.tag("br"));
        this.element.appendChild(this.timeLeft);
        this.printTimeLeft();
        // this.span.innerText = new Date().toUTCString();
    }
    printTimeLeft() {
        var milliSecs = this.endDate.getTime() - new Date().getTime();
        this.secSpan.innerHTML = "Seconds left: " + Math.floor(milliSecs / 1000);
        this.hourSpan.innerHTML = "Hours left: " + Math.floor(milliSecs / 3600000);
        this.timeLeft.innerHTML = "Time left: " + this.toDate(milliSecs);
    }
    toNiceString(number) {
        var str = number.toString();
        if (str.length < 2) {
            return "0" + str;
        }
        else {
            return str;
        }
    }
    toDate(milliSec) {
        // var milliSec = date.getTime();
        let prefix = "";
        if (milliSec < 0) {
            milliSec *= -1;
            prefix = "-";
        }
        var secs = milliSec / 1000;
        var minutes = secs / 60;
        var hours = minutes / 60;
        var days = Math.floor(hours / 24);
        return prefix
            + days + " "
            + this.toNiceString(Math.floor(hours % 24))
            + ":" + this.toNiceString(Math.floor(minutes % 60))
            + ":" + this.toNiceString(Math.floor(secs % 60));
    }
    start() {
        this.timerToken = setInterval(() => {
            this.printTimeLeft();
        }, 500);
    }
    stop() {
        clearTimeout(this.timerToken);
    }
}
window.onload = () => {
    var el = document.getElementById("content");
    var el2 = document.getElementById("time2");
    var greeter = new CountDown(el, new Date(2017, 5, 30, 12, 0, 0), "drivable car");
    var greeter2 = new CountDown(el2, new Date(2017, 5, 2, 15, 0, 0), "Design Spec Sheet");
    greeter.start();
    greeter2.start();
    let eng_div = document.getElementById("england");
    let ger_div = document.getElementById("germany");
    let comp_eng = new Competition(eng_div, "England", handIns_eng);
    comp_eng.make();
    let comp_ger = new Competition(ger_div, "Tyskland", handIns_ger);
    comp_ger.make();
    let body = document.body;
    let outerwrapper = document.getElementById("outer-wrapper");
    let wrapperCount = document.getElementsByClassName("wrapper").length;
    outerwrapper.style.width = wrapperCount + "00%";
    let clock = new Clock(document.getElementsByClassName("clock")[0]);
    let cdWrapper = document.createElement("div");
    let cd = new CountDown(cdWrapper, new Date(2019, 11, 15, 16, 0, 0), "Design Lock!");
    cd.start();
    document.getElementById("designlock").appendChild(cdWrapper);
};
class Clock {
    constructor(element) {
        this.element = element;
        let mk = new HtmlHelper();
        let now = new Date();
        this.time = mk.tag("div", "", null, now.toLocaleTimeString("nb-NO"));
        this.date = mk.tag("div", "clock-date", null, now.toLocaleDateString("nb-NO"));
        console.log(element);
        this.element.appendChild(this.time);
        this.element.appendChild(this.date);
        setInterval(() => { this.tick(); }, 1000);
    }
    tick() {
        this.time.innerHTML = new Date().toLocaleTimeString("nb-NO");
    }
}
var selectedSpan = null;
class HtmlHelper {
    tag(tag, className = "", events = null, innerHTML = "") {
        return HtmlHelper.tag(tag, className, events, innerHTML);
    }
    static tag(tag, className = "", events = null, innerHTML = "") {
        let temp = document.createElement(tag);
        temp.className = className;
        temp.innerHTML = innerHTML;
        if (events != null) {
            for (var i = 0; i < events.length; i++) {
                temp.addEventListener(events[i].event, events[i].func);
            }
        }
        return temp;
    }
}
class HtmlTableGen {
    constructor(className = "", resizeable = false) {
        this.header = [];
        this.rows = [];
        this.resizeable = false;
        this.className = className;
        this.resizeable = resizeable;
    }
    addHeader(...fields) {
        this.header = fields;
    }
    addRow(...columns) {
        this.rows.push(columns);
    }
    addArrayRow(row) {
        this.rows.push(row);
    }
    addArray(data, keys = null, check = null) {
        if (check == null) {
            check = (value) => { return true; };
        }
        for (var i = 0; i < data.length; i++) {
            let row = [];
            if (keys == null) {
                keys = Object.keys(data[i]);
            }
            if (check(data[i])) {
                for (let j = 0; j < keys.length; j++) {
                    row.push(data[i][keys[j]]);
                }
                this.addArrayRow(row);
            }
        }
    }
    generate() {
        var table = document.createElement("table");
        if (this.className != null) {
            table.className = this.className;
        }
        if (this.header.length > 0) {
            var thead = document.createElement("thead");
            var headerRow = document.createElement("tr");
            for (var i = 0; i < this.header.length; i++) {
                var header = document.createElement("th");
                header.innerHTML = this.header[i];
                headerRow.appendChild(header);
                if (this.resizeable) {
                    let span = document.createElement("span");
                    span.className = "table-resize";
                    span.addEventListener("mousedown", (e) => {
                        span.deltaX = span.parentElement.offsetWidth - e.pageX;
                        selectedSpan = span;
                    });
                    header.appendChild(span);
                }
            }
            thead.appendChild(headerRow);
            table.appendChild(thead);
        }
        var rows = this.rows;
        for (var row = 0; row < rows.length; row++) {
            var curRow = rows[row];
            var rowEle = document.createElement("tr");
            for (var col = 0; col < curRow.length; col++) {
                if (Array.isArray(this.rows[row][col])) {
                    for (var i = 0; i < this.rows[row][col].length; i++) {
                        if (this.rows[row][col][i].event != null) {
                            rowEle.addEventListener(this.rows[row][col][i].event, this.rows[row][col][i].func);
                        }
                        else if (this.rows[row][col][i].field != null) {
                            rowEle[this.rows[row][col][i].field] = this.rows[row][col][i].data;
                        }
                    }
                }
                else {
                    var colEle = document.createElement("td");
                    colEle.innerHTML = this.rows[row][col];
                    rowEle.appendChild(colEle);
                }
            }
            table.appendChild(rowEle);
        }
        return table;
    }
}
class Competition {
    constructor(wrapper, title, handIns) {
        this.mk = new HtmlHelper();
        this.wrapper = wrapper;
        this.handIns = handIns;
        this.title = title;
    }
    make() {
        this.table = new HtmlTableGen("table");
        this.table.addHeader("Tittel", "Dato", "Ansvar", "Levert", "Godkjent");
        for (let h of this.handIns) {
            let resp = "";
            switch (h.responsibility) {
                case Responsibility.Undefined:
                    break;
                case (Responsibility.E | Responsibility.M):
                    resp = "M/E";
                    break;
                case Responsibility.M:
                    resp = "M";
                    break;
                case Responsibility.E:
                    resp = "E";
                    break;
                case Responsibility.D:
                    resp = "D";
                    break;
            }
            let CB_delivered = this.mk.tag("input");
            CB_delivered.type = "checkbox";
            CB_delivered.checked = h.delivered;
            let CB_approved = this.mk.tag("input");
            CB_approved.checked = h.approved;
            CB_approved.type = "checkbox";
            this.table.addRow(h.title, h.deadline.toDateString(), resp, h.delivered ? "&#9745;" : "&#9744;", h.approved ? "&#9745;" : "&#9744;");
        }
        let t = this.table.generate();
        this.wrapper.appendChild(this.mk.tag("h1", "", null, this.title));
        this.wrapper.appendChild(t);
    }
}
var Responsibility;
(function (Responsibility) {
    Responsibility[Responsibility["Undefined"] = 1] = "Undefined";
    Responsibility[Responsibility["M"] = 2] = "M";
    Responsibility[Responsibility["E"] = 4] = "E";
    Responsibility[Responsibility["D"] = 8] = "D";
})(Responsibility || (Responsibility = {}));
let handIns_eng = [
    {
        title: "ESA & ESO",
        deadline: new Date(2019, 0, 30),
        delivered: true,
        responsibility: Responsibility.E,
        approved: false
    },
    {
        title: "FMEA",
        deadline: new Date(2019, 0, 30),
        delivered: true,
        responsibility: Responsibility.E,
        approved: false
    },
    {
        title: "SES",
        deadline: new Date(2019, 0, 30),
        delivered: true,
        responsibility: (Responsibility.E | Responsibility.M),
        approved: true
    },
    {
        title: "IAD",
        deadline: new Date(2019, 1, 21),
        delivered: true,
        responsibility: Responsibility.M,
        approved: false
    },
    {
        title: "ESF",
        deadline: new Date(2019, 2, 20),
        delivered: true,
        responsibility: Responsibility.E,
        approved: false
    },
    {
        title: "Essential info online form - Part 1",
        deadline: new Date(2019, 3, 21),
        delivered: true,
        responsibility: Responsibility.Undefined,
        approved: false
    },
    {
        title: "Essential info online form - Part 2",
        deadline: new Date(2019, 3, 21),
        delivered: true,
        responsibility: Responsibility.Undefined,
        approved: false
    },
    {
        title: "Design Report",
        deadline: new Date(2017, 9, 8),
        delivered: true,
        responsibility: Responsibility.Undefined,
        approved: false
    },
    {
        title: "Design Spec Sheet",
        deadline: new Date(2019, 4, 8),
        delivered: true,
        responsibility: Responsibility.Undefined,
        approved: false
    },
    {
        title: "Cost Report & eBom",
        deadline: new Date(2019, 4, 26),
        delivered: true,
        responsibility: (Responsibility.E | Responsibility.M),
        approved: false
    },
    {
        title: "Payment for additional members",
        deadline: new Date(2019, 4, 26),
        delivered: false,
        responsibility: Responsibility.Undefined,
        approved: false
    }
];
let handIns_ger = [
    {
        title: "ESF Components",
        deadline: new Date(2019, 2, 17),
        delivered: true,
        responsibility: Responsibility.E,
        approved: false
    },
    {
        title: "Impact Attenuator Data",
        deadline: new Date(2019, 2, 17),
        delivered: true,
        responsibility: Responsibility.M,
        approved: false
    },
    {
        title: "Structural Equivalency 3D Model",
        deadline: new Date(2019, 2, 17),
        delivered: true,
        responsibility: Responsibility.M,
        approved: true
    },
    {
        title: "SES",
        deadline: new Date(2019, 2, 17),
        delivered: true,
        responsibility: Responsibility.M,
        approved: true
    },
    {
        title: "ESF",
        deadline: new Date(2019, 3, 14),
        delivered: true,
        responsibility: Responsibility.E,
        approved: false
    },
    {
        title: "SES Approval",
        deadline: new Date(2019, 3, 14),
        delivered: true,
        responsibility: Responsibility.Undefined,
        approved: true
    },
    {
        title: "Business Plan Excecutive Summary",
        deadline: new Date(2019, 5, 2),
        delivered: false,
        responsibility: Responsibility.Undefined,
        approved: false
    },
    {
        title: "Design Spec Sheet",
        deadline: new Date(2019, 5, 2),
        delivered: false,
        responsibility: Responsibility.Undefined,
        approved: false
    },
    {
        title: "Engineering Design Report",
        deadline: new Date(2019, 5, 2),
        delivered: false,
        responsibility: Responsibility.Undefined,
        approved: false
    },
    {
        title: "Charging Connector and Power",
        deadline: new Date(2019, 5, 16),
        delivered: false,
        responsibility: Responsibility.Undefined,
        approved: false
    },
    {
        title: "Electrical System Officer Qualification",
        deadline: new Date(2019, 5, 16),
        delivered: false,
        responsibility: Responsibility.Undefined,
        approved: false
    },
    {
        title: "Team Member Designation",
        deadline: new Date(2019, 5, 16),
        delivered: false,
        responsibility: Responsibility.Undefined,
        approved: false
    },
    {
        title: "Vehicle Status Video",
        deadline: new Date(2019, 5, 30),
        delivered: false,
        responsibility: Responsibility.Undefined,
        approved: false
    },
    {
        title: "Cost Report Document",
        deadline: new Date(2019, 6, 21),
        delivered: false,
        responsibility: Responsibility.Undefined,
        approved: false
    }
    ,
    {
        title: "Concept Presentation",
        deadline: new Date(2019, 10, 5),
        delivered: false,
        responsibility: Responsibility.Undefined,
        approved: false
    }

];
//# sourceMappingURL=app.js.map
