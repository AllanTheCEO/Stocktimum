import { useEffect, useRef, useState } from 'react';
import Chart from 'chart.js/auto';
import 'chartjs-adapter-date-fns';
import { stocksList } from './stocksList';

const tableStyles = {
  table: {
    borderCollapse: 'collapse',
    width: '80%',
    margin: '20px auto'
  },
  headerCell: {
    border: '1px solid #ddd',
    padding: '8px',
    backgroundColor: '#f2f2f2'
  },
  bodyCell: {
    border: '1px solid #ddd',
    padding: '8px',
    color: 'white'
  }
};

const getDisplayUnit = (period) => (period === '5y' || period === '10y' ? 'month' : 'day');

function App() {
  const [ticker, setTicker] = useState('AAPL');
  const [period, setPeriod] = useState('10y');
  const [interval, setInterval] = useState('1d');
  const [rows, setRows] = useState([]);
  const [message, setMessage] = useState('Loading...');
  const [error, setError] = useState('');
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);

  useEffect(() => {
    fetch('/api/hello')
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((err) => setMessage(`Error: ${err}`));
  }, []);

  const updateChart = async (nextTicker, nextPeriod, nextInterval) => {
    setError('');
    const url = `/api/data?ticker=${nextTicker}&period=${nextPeriod}&interval=${nextInterval}`;

    try {
      const response = await fetch(url);
      const data = await response.json();
      const dates = data[0] ?? [];
      const opens = data[1] ?? [];
      const highs = data[2] ?? [];
      const lows = data[3] ?? [];
      const closes = data[4] ?? [];
      const volumes = data[5] ?? [];

      const nextRows = dates.map((date, index) => ({
        date,
        open: opens[index],
        high: highs[index],
        low: lows[index],
        close: closes[index],
        volume: volumes[index]
      }));
      setRows(nextRows);

      if (!chartRef.current) {
        return;
      }

      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }

      chartInstanceRef.current = new Chart(chartRef.current.getContext('2d'), {
        type: 'line',
        data: {
          labels: dates,
          datasets: [
            {
              label: `${nextTicker} Price`,
              data: closes,
              borderColor: 'rgb(192, 75, 75)',
              backgroundColor: 'rgba(13, 89, 220, 0.2)',
              fill: false,
              tension: 0.1
            }
          ]
        },
        options: {
          plugins: {
            tooltip: {
              enabled: false
            }
          },
          scales: {
            x: {
              type: 'time',
              time: {
                unit: getDisplayUnit(nextPeriod)
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
      });
    } catch (fetchError) {
      console.error('Error fetching data:', fetchError);
      setError('Unable to load stock data.');
    }
  };

  useEffect(() => {
    updateChart(ticker, period, interval);
  }, []);

  return (
    <div>
      <h1>Stock Forecasting Dashboard</h1>
      <p>{message}</p>
      {error ? <p>{error}</p> : null}
      <div className="container">
        <div className="sidebar">
          <h2>Adjust Stock Parameters</h2>
          <div>
            <label htmlFor="tickerSelect">Stock:</label>
            <select
              id="tickerSelect"
              value={ticker}
              onChange={(event) => setTicker(event.target.value)}
            >
              <option value=""></option>
              {stocksList.map((stock) => (
                <option key={stock} value={stock}>
                  {stock}
                </option>
              ))}
            </select>

            <label htmlFor="periodSelect">Period:</label>
            <select
              id="periodSelect"
              value={period}
              onChange={(event) => setPeriod(event.target.value)}
            >
              <option value="1mo">1mo</option>
              <option value="6mo">6mo</option>
              <option value="1y">1y</option>
              <option value="5y">5y</option>
              <option value="10y">10y</option>
            </select>

            <label htmlFor="intervalSelect">Interval:</label>
            <select
              id="intervalSelect"
              value={interval}
              onChange={(event) => setInterval(event.target.value)}
            >
              <option value="1d">1d</option>
              <option value="1wk">1wk</option>
              <option value="1mo">1mo</option>
            </select>

            <button
              id="updateChart"
              type="button"
              onClick={() => updateChart(ticker, period, interval)}
            >
              Update Chart
            </button>
          </div>
        </div>

        <div className="content">
          <div className="chart-container">
            <h2>Raw data</h2>
            <div id="priceTable">
              <table style={tableStyles.table}>
                <thead>
                  <tr>
                    {['Date', 'Open', 'High', 'Low', 'Close', 'Volume'].map((header) => (
                      <th key={header} style={tableStyles.headerCell}>
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody id="priceTableBody">
                  {rows.map((row, index) => (
                    <tr key={`${row.date}-${index}`}>
                      <td style={tableStyles.bodyCell}>{row.date}</td>
                      <td style={tableStyles.bodyCell}>{row.open}</td>
                      <td style={tableStyles.bodyCell}>{row.high}</td>
                      <td style={tableStyles.bodyCell}>{row.low}</td>
                      <td style={tableStyles.bodyCell}>{row.close}</td>
                      <td style={tableStyles.bodyCell}>{row.volume}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="table-container">
            <h2>Stock Price Chart</h2>
            <canvas id="priceChart" ref={chartRef}></canvas>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
