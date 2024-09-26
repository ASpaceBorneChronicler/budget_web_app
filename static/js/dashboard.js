/* globals Chart:false */
// will just have to re do it in pychart.js
(() => {
  'use strict'
//        var income_data = {{ incomeChart | safe }};
//    console.log(income_data)
//    var expense_data = {{ expenseChart | safe }};
    var income_ctx = document.getElementById("income_chart").getContext('2d');
//    var expense_ctx = document.getElementById("expense_chart");
    var income_chart = new Chart(income_ctx,
    {
  type: "doughnut",
  data: {
    labels: ['Salary', 'Side hustle'],
    datasets: [
      {
        id: "Salary",
        nested: {
            value: 100000
        }
    },
    {
        id: "side hustle",
        nested: {
            value: 500000
        }
    }
    ]
  },
  options: {
    parsing: {
      key: nested.value
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
//    var expense_chart = new Chart(expense_ctx, expense_data);
  // eslint-disable-next-line no-unused-vars
//  const myChart = new Chart(ctx, {
//    type: 'line',
//    data: {
//      labels: [
//        'Sunday',
//        'Monday',
//        'Tuesday',
//        'Wednesday',
//        'Thursday',
//        'Friday',
//        'Saturday'
//      ],
//      datasets: [{
//        data: [
//          15339,
//          21345,
//          18483,
//          24003,
//          23489,
//          24092,
//          12034
//        ],
//        lineTension: 0,
//        backgroundColor: 'transparent',
//        borderColor: '#007bff',
//        borderWidth: 4,
//        pointBackgroundColor: '#007bff'
//      }]
//    },
//    options: {
//      plugins: {
//        legend: {
//          display: false
//        },
//        tooltip: {
//          boxPadding: 3
//        }
//      }
//    }
//  })
})()
