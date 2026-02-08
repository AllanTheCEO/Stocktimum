import { stocksList } from './stocks.js';


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
      plugins: {
        tooltip: {
          enabled: false,
          /*
          backgroundColor: "rgba(156, 187, 161, 0.5)",
          title: function(tooltipItems) {
            return 'x';
          },*/
        } 
      },
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
        const opens = data[1];
        const highs = data[2];
        const lows = data[3];
        const closes = data[4];
        const volumes = data[5];

        // Update the config with new data and label
        config.data.labels = dates;
        config.data.datasets[0].data = closes;
        config.data.datasets[0].label = `${ticker} Price`;

        // Get the canvas context
        const ctx = document.getElementById('priceChart').getContext('2d');

        // If a chart already exists, destroy it before creating a new one.
        if (chartInstance) {
          chartInstance.destroy();
        }
        chartInstance = new Chart(ctx, config);
        // --- Update Table ---
      // Clear the existing table container.
      const tableContainer = document.getElementById('priceTable');
      tableContainer.innerHTML = '';

      // Create a new table element.
      const table = document.createElement('table');
      table.style.borderCollapse = 'collapse';
      table.style.width = '80%';
      table.style.margin = '20px auto';

      // Create table header.
      const thead = document.createElement('thead');
      const headerRow = document.createElement('tr');
      const headers = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume'];
      headers.forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        th.style.border = '1px solid #ddd';
        th.style.padding = '8px';
        th.style.backgroundColor = '#f2f2f2';
        headerRow.appendChild(th);
      });
      thead.appendChild(headerRow);
      table.appendChild(thead);

      // Create table body.
      const tbody = document.createElement('tbody');
      tbody.id = 'priceTableBody';

      // Populate the table rows using the fetched array values.
      for (let i = 0; i < dates.length; i++) {
        const row = document.createElement('tr');

        // Create cells for each column using the fetched data.
        const cellValues = [dates[i], opens[i], highs[i], lows[i], closes[i], volumes[i]];
        cellValues.forEach(value => {
          const td = document.createElement('td');
          td.textContent = value;
          td.style.border = '1px solid #ddd';
          td.style.padding = '8px';
          td.style.color = 'white';
          row.appendChild(td);
        });
        tbody.appendChild(row);
      }

      table.appendChild(tbody);
      tableContainer.appendChild(table);
      })

      .catch(error => console.error('Error fetching data:', error));

  }

  const tickerSelect = document.getElementById('tickerSelect');
  tickerSelect.innerHTML = '';
  const emptyOption = document.createElement('option');
  emptyOption.value = '';
  emptyOption.textContent = '';
  tickerSelect.appendChild(emptyOption);
  
  stocksList.forEach(stock => {
    const option = document.createElement('option');
    option.value = stock;
    option.textContent = stock;
    tickerSelect.appendChild(option);
  });
  
  // jQuery and Select2 are loaded via CDN in HTML
  $(tickerSelect).select2({
    placeholder: 'Select a stock',
    allowClear: true,
    width: 'resolve'
  });

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

  
  
  
  
});
