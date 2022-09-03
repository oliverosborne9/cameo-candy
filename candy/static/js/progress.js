function changeProgVals(data, col) {
    document.getElementById("progressbar" + col).innerHTML = (data + "%");
    document.getElementById("progressbar" + col).ariaValueNow = data;
    document.getElementById("progressbar" + col).style.width = (data + "%");
    if (data != "100") {
        setTimeout(function () { updateProgress(col); }, 500);
    }
};

function updateProgress(col) {
    let taskID = document.getElementById("taskid" + col).getAttribute("uid");
    let progURL = "/task/" + taskID;

    $.ajax({
        type: "GET",
        url: progURL,
        success: function (data) {
            changeProgVals(data, col);
        }
    })

};

function updateProgressAll() {
    let cols = document.getElementById("colours").getAttribute("uid").split("_");
    cols.map(updateProgress)
}

document.addEventListener("DOMContentLoaded", updateProgressAll);
