/* static/js/dashboard.js */

(function () {
  "use strict";

  function downloadTextFile(filename, text, mimeType) {
    var blob = new Blob([text], { type: mimeType || "text/plain;charset=utf-8" });
    var url = URL.createObjectURL(blob);

    var a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    URL.revokeObjectURL(url);
  }

  $(function () {
    if (!window.dashboardData || !Array.isArray(window.dashboardData.labels) || !Array.isArray(window.dashboardData.values)) {
      console.error("window.dashboardData not found. Make sure dashboard.html injects labels/values before loading dashboard.js.");
      return;
    }

    if (typeof Chart === "undefined") {
      console.error("Chart.js not loaded. Ensure Chart.js is included before dashboard.js.");
      return;
    }

    var labels = window.dashboardData.labels;
    var values = window.dashboardData.values;

    var canvas = document.getElementById("trendChart");
    if (!canvas) {
      console.error("Canvas #trendChart not found.");
      return;
    }

    var chart = new Chart(canvas, {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: "Metric",
          data: values,
          borderWidth: 2,
          tension: 0.35,
          pointRadius: 3
        }]
      },
      options: {
        responsive: true,
        scales: { y: { beginAtZero: true } }
      }
    });

    $("#btnRandomize").on("click", function () {
      var newVals = chart.data.datasets[0].data.map(function () {
        return Math.floor(Math.random() * 100);
      });

      chart.data.datasets[0].data = newVals;
      chart.update();

      var total = newVals.reduce(function (a, b) { return a + b; }, 0);
      var avg = (total / newVals.length).toFixed(1);
      var max = Math.max.apply(null, newVals);

      $("#kpiTotal").text(total);
      $("#kpiAvg").text(avg);
      $("#kpiMax").text(max);
    });

    $("#btnExport").on("click", function () {
      var csv = "date,metric\n";
      for (var i = 0; i < chart.data.labels.length; i++) {
        csv += chart.data.labels[i] + "," + chart.data.datasets[0].data[i] + "\n";
      }
      downloadTextFile("export.csv", csv, "text/csv;charset=utf-8");
    });
  });
})();