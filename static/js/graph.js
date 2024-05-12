var lineSeries;
var colour;
var chart;

function updateChartWithData(newData,flag) {

    let firstDataTime = newData[0].time;
    let lastDataTime = newData[newData.length - 1].time;
    const dom = document.getElementById('chart_result');

    // console.log("Updating chart with new data:", newData);

    if (flag == -1) { colour = '#cd2323' }
    else { colour = '#00b386' }
    if (lineSeries) {
        chart.removeSeries(lineSeries);
    }
    lineSeries = chart.addLineSeries({ color: colour,lineWidth: 1.8});
    lineSeries.setData(newData);

    
    // Set the visible range for the time scale
    chart.timeScale().setVisibleRange({ from: firstDataTime, to: lastDataTime });
    function resizeChart() {
        chart.applyOptions({ width: dom.clientWidth, height: dom.clientHeight });
    }

    window.addEventListener('resize', resizeChart);
    resizeChart();

}
document.addEventListener('DOMContentLoaded', function () {
    // Get the container element
    const dom = document.getElementById('chart_result');

    // Chart properties
    let  properties = {
        layout: {
            backgroundColor: '#000000',
            textColor: '#131722',
        },
        grid: {
            vertLines: {
                color: 'transparent',
            },
            horzLines: {
                color: 'transparent',
            },
        },
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
            borderColor: 'transparent',
        },
        rightPriceScale: {
            visible: false,
            drawTicks: false,
        },
        leftPriceScale: {
            visible: true,
            borderColor: 'transparent',
            drawTicks: false,
            
        },
        handleScroll: {
            mouseWheel: false,
            pressedMouseMove: false,
            horzTouchDrag: false,
            vertTouchDrag: false
        },
        handleScale: {
            axisPressedMouseMove: false,
            mouseWheel: false,
            pinch: false,
        },
        

        
    };

    // Create a new chart
    chart = LightweightCharts.createChart(dom, properties);
    if (flag == -1) { colour = '#cd2323' }
    else { colour = '#00b386' }
    // Add a line series to the chart
    lineSeries = chart.addLineSeries({ color: colour,lineWidth: 1.8});

    

    // Add data to the line series
    lineSeries.setData(graphdata);

    // Customize crosshair
    chart.applyOptions({
        crosshair: {
            
            vertLine: {
                color: 'rgba(0, 0, 0, 0.5)', // Color of the vertical line
                width: 2, // Width of the vertical line
                style: 1, // Style of the vertical line (1: solid)
                visible: true, // Make the vertical line visible
                labelVisible: true, // Show value label on hover
            },
            horzLine: {
                visible: false, // Make the horizontal line invisible
            },
            
        },
    });


    const firstDataTime = graphdata[0].time;
    const lastDataTime = graphdata[graphdata.length - 1].time;

    // Set the visible range for the time scale
    chart.timeScale().setVisibleRange({ from: firstDataTime, to: lastDataTime });
    function resizeChart() {
        chart.applyOptions({ width: dom.clientWidth, height: dom.clientHeight });
    }

    window.addEventListener('resize', resizeChart);
    resizeChart(); // Initial sizing
    // Ensure that the chart covers the full range of the data

    document.getElementById('chart_result').addEventListener('touchmove', e => {
        const bcr = document.getElementById('chart_result').getBoundingClientRect();
        const x = bcr.left + e.touches[0].clientX;
        const y = bcr.top + e.touches[0].clientY;
    
        const price = lineSeries.coordinateToPrice(y);
        const time = chart.timeScale().coordinateToTime(x);
    
        if (!Number.isFinite(price) || !Number.isFinite(time)) {
            return;
        }
    
        chart.setCrosshairPosition(price, time, lineSeries);
    });
    
    document.getElementById('chart_result').addEventListener('touchend', () => {
        chart.clearCrosshairPosition();
    });
    

    
});

