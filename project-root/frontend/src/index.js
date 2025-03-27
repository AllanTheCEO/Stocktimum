document.addEventListener('DOMContentLoaded', () => {
  let chartInstance = null;

  // Constant configuration object – we'll update its data when new values are fetched.

  const config = {
    type: 'line',
    data: {
      labels: [], // Dates will go here
      datasets: [{
        label: 'Stock Price',
        data: [],  // Prices will go here
        borderColor: 'rgb(192, 75, 75)',
        backgroundColor: 'rgba(13, 89, 220, 0.2)',
        fill: false,
        tension: 0.1
      }]
    },
    options: {
      scales: {
        x: {
          type: 'time', // Use time scale for the x-axis
          time: {
            unit: updateChart.getDisplayDates
          },
          title: {
            display: true,
            text: 'Date'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Price (USD)'
          }
        }
      }
    }
  };

  // Function to fetch new data and update the chart using the constant config.
  function updateChart(ticker, period, interval) {
    const url = `/api/data?ticker=${ticker}&period=${period}&interval=${interval}`;

    function getDisplayDates(period) {
        if(period == '5y' || period == '10y') {
            return 'month'
        } else {
            return 'day'
        }
      }

    fetch(url)
      .then(response => response.json())
      .then(data => {
        // Assume data is in the form: [ [ '2025-03-18', ... ], [212.69, ...] ]
        const dates = data[0];
        const prices = data[1];

        // Update the config with new data and label
        config.data.labels = dates;
        config.data.datasets[0].data = prices;
        config.data.datasets[0].label = `${ticker} Price`;

        // Get the canvas context
        const ctx = document.getElementById('priceChart').getContext('2d');

        // If a chart already exists, destroy it before creating a new one.
        if (chartInstance) {
          chartInstance.destroy();
        }
        chartInstance = new Chart(ctx, config);
      })
      .catch(error => console.error('Error fetching data:', error));
  }

  // Get the UI elements for user input
  const tickerSelect = document.getElementById('tickerSelect');
  const periodSelect = document.getElementById('periodSelect');
  const intervalSelect = document.getElementById('intervalSelect');
  const updateChartBtn = document.getElementById('updateChart');

  // Render the initial chart using default values
  updateChart(tickerSelect.value, periodSelect.value, intervalSelect.value);

  // Update the chart when the user clicks the button
  updateChartBtn.addEventListener('click', () => {
    const selectedTicker = tickerSelect.value;
    const selectedPeriod = periodSelect.value;
    const selectedInterval = intervalSelect.value;
    updateChart(selectedTicker, selectedPeriod, selectedInterval);
  });

  // createTable fetches data from the API and creates a Chart.js chart.
  // It expects the API to return an array: 
  // [dates, openPrices, highPrices, lowPrices, closePrices, volume]
  function createTable(ticker, period, interval) {
    const url = `/api/data?ticker=${ticker}&period=${period}&interval=${interval}`;
  
    fetch(url)
      .then(response => response.json())
      .then(data => {
        // Destructure the returned data
        const [dates, opens, highs, lows, closes, volumes] = data;
  
        // Grab the table body
        const tableBody = document.getElementById("priceTableBody");
        // Clear out any existing rows
        tableBody.innerHTML = "";
  
        // Loop through the data arrays and build rows
        for (let i = 0; i < dates.length; i++) {
          const row = document.createElement("tr");
  
          // Create cells for each column
          const dateCell = document.createElement("td");
          dateCell.textContent = dates[i];
          row.appendChild(dateCell);
  
          const openCell = document.createElement("td");
          openCell.textContent = opens[i];
          row.appendChild(openCell);
  
          const highCell = document.createElement("td");
          highCell.textContent = highs[i];
          row.appendChild(highCell);
  
          const lowCell = document.createElement("td");
          lowCell.textContent = lows[i];
          row.appendChild(lowCell);
  
          const closeCell = document.createElement("td");
          closeCell.textContent = closes[i];
          row.appendChild(closeCell);
  
          const volumeCell = document.createElement("td");
          volumeCell.textContent = volumes[i];
          row.appendChild(volumeCell);
  
          // Append the new row to the table body
          tableBody.appendChild(row);
        }
      })
      .catch(error => console.error("Error fetching data:", error));
    }
  
});
