const canvas = document.querySelector("#canvas");
const ctx = canvas.getContext('2d');
const borderPad = 20;

// var myApp = {}; //globally scoped object
// myApp.metricEvent = setInterval(updateShadedMetrics, 1000);

var windowWidth = $(window).width();

let painting = false;
let clr = "red";
var mouse = true;

function submitButtonEnabled(bool) {
    document.getElementById("button").disabled = !bool;
}

const redIntensity = parseInt(document.getElementById("redIntensity").getAttribute("intensity"));
const greenIntensity = parseInt(document.getElementById("greenIntensity").getAttribute("intensity"));
const blueIntensity = parseInt(document.getElementById("blueIntensity").getAttribute("intensity"));
const redCapacity = parseInt(document.getElementById("redCapacity").getAttribute("capacity"));
const greenCapacity = parseInt(document.getElementById("greenCapacity").getAttribute("capacity"));
const blueCapacity = parseInt(document.getElementById("blueCapacity").getAttribute("capacity"));

function initialSetup() {
    const startBrushWidth = Math.min(Math.floor(windowWidth / 40), 50);
    document.getElementById("brush-width-range").value = startBrushWidth;
    canvasSetup();
}

function smartCanvasSetup() {
    var newWindowWidth = $(window).width();
    if (newWindowWidth != windowWidth) {
        windowWidth = newWindowWidth;
        canvasSetup();
    }
}

function canvasSetup() {

    canvas.width = container.clientWidth - 25;
    var smartHeight = Math.min(Math.floor(container.clientWidth * 3 / 4), (window.innerHeight - 385));
    canvas.height = Math.max(smartHeight, 220);


    // White background
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);


    // Draw Frame
    ctx.beginPath();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "black";
    ctx.rect(borderPad, borderPad, canvas.width - borderPad * 2, canvas.height - borderPad * 2);
    ctx.stroke();
    endPosition();

    changeColour(clr);
}


window.addEventListener('load', initialSetup);
window.addEventListener('resize', smartCanvasSetup);

function getPos(canvas, e) {
    var rect = canvas.getBoundingClientRect();
    var f = e
    if (mouse != true) {
        f = f.touches[0]
    }
    return {
        x: f.clientX - rect.left,
        y: f.clientY - rect.top
    };
}

function startPosition(e) {
    e.preventDefault();
    painting = true;
    draw(e, mouse);
}

function endPosition() {
    painting = false;
    ctx.beginPath();
    updateShadedMetrics();
}

function draw(e) {
    if (!painting) return;
    e.preventDefault();

    ctx.lineWidth = $("#brush-width-range").val();
    ctx.lineCap = "round";

    var pos = getPos(canvas, e);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
}

// SAFARI HACK for iPhone
// + {passive: false}
// + e.preventDefault();
function stopScroll(e) {
    if (e.target == canvas) {
        e.preventDefault();
    }
}
// canvas.addEventListener("touchmove", stopScroll);

['mousedown', 'touchstart'].forEach(evt =>
    canvas.addEventListener(evt, startPosition, { passive: false })
);
['mousemove', 'touchmove'].forEach(evt =>
    canvas.addEventListener(evt, draw, { passive: false })
);
['mouseup', 'touchend'].forEach(evt =>
    canvas.addEventListener(evt, endPosition)
);

canvas.addEventListener("touchstart", function () {
    mouse = false
});


function changeColour(colour) {
    const xlink = "http://www.w3.org/1999/xlink";
    const bootstrap_icon = "/bootstrap/static/icons/bootstrap-icons.svg#";
    clr = colour;
    ctx.strokeStyle = colour;
    if (colour == "rgb(255,255,255)") {
        document.getElementById("paintbrush").style.color = "rgb(0,0,0)";
        document.getElementById("icon-use").setAttributeNS(xlink, 'xlink:href', bootstrap_icon + "eraser-fill");
    } else {
        document.getElementById("paintbrush").style.color = colour;
        document.getElementById("icon-use").setAttributeNS(xlink, 'xlink:href', bootstrap_icon + "brush-fill");
    }
}

$('#button').on('click', function (e) {
    $('#loadingModal').modal('show');
    var dataURL = canvas.toDataURL();
    var shadedDict = getColourShaded();
    var capacityDict = getCapacityFromPct(shadedDict);

    $.ajax({
        type: "POST",
        url: "/submit",
        data: {
            imageBase64: dataURL,
            quantities: JSON.stringify(
                {
                    red: capacityDict.r,
                    green: capacityDict.g,
                    blue: capacityDict.b
                }
            )
        },
    }).done(function (_, status) {
        if (status == "success") {
            location.href = "/progress"
            console.log(status)
        } else {
            $('#loadingModal').modal('hide');
            // ALERT
        }
    })
});

function changeProgVals(data, col) {
    document.getElementById("progressbar" + col).innerHTML = (data + "%");
    document.getElementById("progressbar" + col).ariaValueNow = data;
    document.getElementById("progressbar" + col).style.width = (data + "%");
}

function getColourShaded() {
    var imgD = ctx.getImageData(0, 0, canvas.width, canvas.height);
    var pix = imgD.data;
    var rgb = { r: 0, g: 0, b: 0 };
    var blockSize = 4;
    var length = pix.length;
    const block = (element) => element == 0;
    for (let i = 0; i < length; i += blockSize) {
        var r = pix[i];
        var g = pix[i + 1];
        var b = pix[i + 2];
        if ([r, g, b].some(block)) {
            rgb.r += r;
            rgb.g += g;
            rgb.b += b;
        }
    }
    rgb.r /= redIntensity;
    rgb.g /= greenIntensity;
    rgb.b /= blueIntensity;

    const full_box = (canvas.width - 2 * borderPad) * (canvas.height - 2 * borderPad);
    rgb.r /= full_box;
    rgb.g /= full_box;
    rgb.b /= full_box;

    return rgb
}

function getCapacityFromPct(rgb) {
    var rG = (rgb.r * redCapacity).toFixed(0);
    var gG = (rgb.g * greenCapacity).toFixed(0);
    var bG = (rgb.b * greenCapacity).toFixed(0);
    return { r: rG, g: gG, b: bG }
}

function setPctSliders(rgb) {
    var rPct = (rgb.r * 100).toFixed(2);
    var gPct = (rgb.g * 100).toFixed(2);
    var bPct = (rgb.b * 100).toFixed(2);

    changeProgVals(rPct, "red");
    changeProgVals(gPct, "green");
    changeProgVals(bPct, "blue");
}

function setCapacityVisuals(rgbG) {
    document.getElementById("red-g").innerText = rgbG.r;
    document.getElementById("green-g").innerText = rgbG.g;
    document.getElementById("blue-g").innerText = rgbG.b;

    myChart.data.datasets[0].data = [rgbG.r, rgbG.g, rgbG.b];
    myChart.update();
}

function validateSubmitButton(capacityDict) {
    var totalRequested = capacityDict.r + capacityDict.g + capacityDict.b;
    submitButtonEnabled(totalRequested > 0);
}

function updateShadedMetrics() {
    var rgbDict = getColourShaded();
    setPctSliders(rgbDict);
    var rgbCapacityDict = getCapacityFromPct(rgbDict);
    validateSubmitButton(rgbCapacityDict);
    setCapacityVisuals(rgbCapacityDict);
}
