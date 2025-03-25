document.addEventListener('DOMContentLoaded', () => {
    // Fetch the 2D array data from the backend
    fetch('http://127.0.0.1:5000/api/data')
      .then(response => response.json())
      .then(data => {
        // Assume data is in the form:
        // [ [ '2025-03-18', '2025-03-19', ... ], [212.69, 215.24, ...] ]
        const dates = data[0];
        const prices = data[1];
  
        // Get the canvas element and its 2d context
        const ctx = document.getElementById('priceChart').getContext('2d');
  
        // Configuration for the Chart.js line chart (based on the official template)
        const config = {
          type: 'line',
          data: {
            labels: dates,  // x-axis: dates
            datasets: [{
              label: 'AAPL Price',
              data: prices,  // y-axis: prices
              borderColor: 'rgb(75, 192, 192)',
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              fill: false,
              tension: 0.1
            }]
          },
          options: {
            scales: {
              x: {
                type: 'time',  // Use the time scale for dates
                time: {
                  unit: 'day'
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
  
        // Create and render the chart
        new Chart(ctx, config);
      })
      .catch(error => console.error('Error fetching data:', error));
  });
  