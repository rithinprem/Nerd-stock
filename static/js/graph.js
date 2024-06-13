var lineSeries;
var colour;
var chart;


function formatDate(date, timeframe='daily') {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    const hours = date.getHours();
    const minutes = date.getMinutes();

    let period = 'AM';
    let adjustedHours = hours;
    if (adjustedHours >= 12) {
        period = 'PM';
        if (adjustedHours > 12) {
            adjustedHours -= 12;
        }
    } else if (adjustedHours === 0) {
        adjustedHours = 12; // Midnight is 12 AM
    }

    const timeStr = `${adjustedHours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')} ${period}`;
    const weekmonSTr = timeStr+','+ `${day} ${month}`;
    const dateStr = `${day} ${month} ${year}`;

    // Adjust the format based on the timeframe
    switch (timeframe) {
        case 'daily':
            return `${timeStr}`; // Show only date for daily charts

        case 'weekly':
            return `${weekmonSTr}`;

        case 'monthly':
            return `${weekmonSTr}`; // Show date and time without seconds for hourly charts

        case '1y':
            return `${dateStr}`;

        case '5y':
            return `${dateStr}`;

        default:
            return `${dateStr}, ${timeStr}`; // Default case
    }
}


function updateChartWithData(newData, flag, time_frame='daily',_firstPrice,current_price,previous_close) {

    let firstDataTime = newData[0].time;
    let lastDataTime = newData[newData.length - 1].time;
    const dom = document.getElementById('chart_result');
    


    if (flag == -1) { 
    colour = '#cd2323';
    document.querySelector('.day_change').innerHTML = '<span style="font-size: 1.2rem;margin-left: 10px;" class="day_change"><i class="fa-solid fa-arrow-down fa-2xs"style="color: #cd2323;"></i><span class="day_value">{{day_change}}</span></span>' }
    else {
    colour = '#00b386';
    document.querySelector('.day_change').innerHTML = '<span style=" font-size: 1.2rem;margin-left: 10px;" class="day_change"><i class="fa-solid fa-arrow-up fa-2xs"style="color: #049f71;"></i><span class="day_value">{{day_change}}</span></span>'}

    if (time_frame=='daily'){document.querySelector(".day_change .day_value").innerHTML =  parseFloat((((current_price - previous_close)/previous_close)*100).toFixed(2))+'%'}
    else{ document.querySelector(".day_change .day_value").innerHTML =  parseFloat((((current_price - _firstPrice)/_firstPrice)*100).toFixed(2))+'%'}

    if (lineSeries) {
        chart.removeSeries(lineSeries);
    }
    lineSeries = chart.addLineSeries({ color: colour, lineWidth: 1.8, crossHairMarkerVisible: false });
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
    let properties = {
        layout: {
            backgroundColor: '#000000',
            textColor: '#949494',
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


    // Customize crosshair
    chart.applyOptions({
        crosshair: {

            vertLine: {
                labelVisible: false,
            },
            horzLine: {
                visible: false, // Make the horizontal line invisible
                labelVisible: false,
            },

        },
    });

    // Add a line series to the chart
    lineSeries = chart.addLineSeries({ color: colour, lineWidth: 1.8, crossHairMarkerVisible: false });


    // Add data to the line series
    lineSeries.setData(graphdata);

    

    const chart_result = document.getElementById('chart_result');

    // Create and style the tooltip html element
    const toolTip = document.getElementById('tooltip');

    // Update tooltip on crosshair move
    function updateTooltip(param) {
        if (
            param.point === undefined ||
            !param.time ||
            param.point.x < 0 ||
            param.point.x > chart_result.clientWidth ||
            param.point.y < 0 ||
            param.point.y > chart_result.clientHeight
        ) {
            toolTip.style.display = 'none';
            return;
        }
        const date = new Date((param.time - 19800) * 1000); // IST
        const tooltipContent = formatDate(date, time_frame);
        toolTip.style.display = 'block';
        const data = param.seriesData.get(lineSeries);
        const price = data.value !== undefined ? data.value : data.close;
        toolTip.innerHTML = `<div style="display: flex; flex-direction: row; align-items: center;"><div><p>₹${price.toFixed(2)}| </p></div><div>${tooltipContent}</div></div>`;
        const toolTipWidth = toolTip.offsetWidth;
        const chartRect = chart_result.getBoundingClientRect();
        let leftPos = param.point.x;

        if (chart_result.clientWidth > 569) {
            if (leftPos >= toolTipWidth / 2 && leftPos < chartRect.right) {
                leftPos = leftPos + 110;
            }

            if (leftPos < chartRect.left) {
                leftPos = chartRect.left;
            }

            if (leftPos + toolTipWidth > chartRect.right) {
                leftPos = chartRect.right - toolTipWidth;
            }
        } else {
            if (leftPos + toolTipWidth > chartRect.right) {
                leftPos = chartRect.right - toolTipWidth;
            }
            if (leftPos < chartRect.left) {
                leftPos = chartRect.left;
            }
            
        }

        toolTip.style.left = `${leftPos}px`;
        toolTip.style.top = toolTip.offsetHeight + 'px';
        chart.timeScale().fitContent();
    }

    chart.subscribeCrosshairMove(updateTooltip);


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

    
   

    document.getElementById('chart_result').addEventListener('touchend', () => {
        chart.clearCrosshairPosition();
        toolTip.innerHTML = `<div></div>`;
    });
});

