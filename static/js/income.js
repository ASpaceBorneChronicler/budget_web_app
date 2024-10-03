/* globals Chart:false */
// will just have to re do it in pychart.js
(() => {
  'use strict'

    var chartOne_ctx = document.getElementById("chartOne");
    var chartTwo_ctx = document.getElementById("chartTwo");
    var chartOne_chart = new Chart(chartOne_ctx,
    {
  type: "doughnut",
  data:  {
        labels: income_data.labels,  // Use labels from income_data
        datasets: [{
          label: "Income Distribution",
          data: income_data.datasets.map(d => d.nested.value),  // Map over the dataset to extract values
          backgroundColor: ['#ff6384', '#36a2eb'],  // Example colors
          borderWidth: 1
        }]
      },
  options: {
    parsing: {
      key: 'nested.value'
    },
    aspectRatio: 2.369747899159664,
    responsive: true,
    padding: 25,
    plugins: {
      legend: {
        position: "right"
      },
      title: {
        display: true,
        text: "Distribution of income",
        position: "top",
        font: {
          weight: "normal",
          size: 16
        },
        align: "start"
      }
    }
  }
});
var chartTwo_chart = new Chart(chartTw_ctx,
    {
  type: "bar",
  data:  {
        labels: expense_data.labels,
        datasets: [{
          label: "Expense Distribution",
          data: expense_data.datasets.map(d => d.nested.value),
          backgroundColor: ['#ff6384', '#36a2eb'],
          borderWidth: 1
        }]
      },
  options: {
    parsing: {
      key: 'nested.value'
    },
    aspectRatio: 2.369747899159664,
    responsive: true,
    padding: 25,
    plugins: {
      legend: {
        position: "right"
      },
      title: {
        display: true,
        text: "Distribution of expenses",
        position: "top",
        font: {
          weight: "normal",
          size: 16
        },
        align: "start"
      }
    }
  }
});
})()