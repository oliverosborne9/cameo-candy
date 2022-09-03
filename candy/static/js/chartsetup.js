Chart.defaults.font.family = '"system-ui","-apple-system","Segoe UI","Roboto","Helvetica Neue","Arial","Noto Sans","Liberation Sans","sans-serif","Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji"'

function getUIDList(elementID) {
    return document.getElementById(elementID).getAttribute("uid");
}

const labelsIDs = ["contentsRed", "contentsGreen", "contentsBlue"];
const barIDs = ["barRed", "barGreen", "barBlue"];

const labels = labelsIDs.map(getUIDList);
const barColors = barIDs.map(getUIDList);
var quantitiesGrams = [0, 0, 0];

var data = {
    labels: labels,
    datasets: [{
        label: "Quantity",
        backgroundColor: barColors,
        borderColor: "black",
        data: quantitiesGrams
    }]
};

const config = {
    type: 'bar',
    data: data,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: true,
                text: "Grams to Dispense"
            },
            legend: {
                display: false
            }
        }
    }
};

var myChart = new Chart(
    document.getElementById('quantityBar'),
    config
);
