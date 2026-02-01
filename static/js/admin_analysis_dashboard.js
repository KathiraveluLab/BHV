document.addEventListener("DOMContentLoaded", function () {
  Chart.register(ChartDataLabels);

  const dataElement = document.getElementById("dashboard-data");
  if (!dataElement) return;

  const DASHBOARD_DATA = JSON.parse(dataElement.textContent);
  const colors = {
    brand: "#0052ff",
    pos: "#10b981",
    neu: "#f59e0b",
    neg: "#ef4444",
  };

  const healthBars = document.querySelectorAll(".js-health-bar");
  healthBars.forEach((bar) => {
    const width = bar.getAttribute("data-width");
    const color = bar.getAttribute("data-color");
    bar.style.width = width + "%";
    bar.style.backgroundColor = color;
  });

  const printBtn = document.getElementById("printReportBtn");
  if (printBtn) {
    printBtn.addEventListener("click", () => window.print());
  }

  const trendCtx = document.getElementById("trendChart");
  if (trendCtx) {
    new Chart(trendCtx, {
      type: "line",
      data: {
        labels: DASHBOARD_DATA.labels,
        datasets: [
          {
            label: "Uploads",
            data: DASHBOARD_DATA.values,
            borderColor: colors.brand,
            backgroundColor: "rgba(0, 82, 255, 0.1)",
            borderWidth: 2,
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          datalabels: { display: false },
        },
        scales: {
          y: { beginAtZero: true, grid: { borderDash: [5, 5] } },
          x: { grid: { display: false } },
        },
      },
    });
  }

  const pieCtx = document.getElementById("pieChart");
  if (pieCtx) {
    new Chart(pieCtx, {
      type: "doughnut",
      data: {
        labels: ["Positive", "Neutral", "Negative"],
        datasets: [
          {
            data: DASHBOARD_DATA.pie,
            backgroundColor: [colors.pos, colors.neu, colors.neg],
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "60%",
        layout: { padding: 20 },
        plugins: {
          legend: { position: "bottom", labels: { boxWidth: 12 } },
          datalabels: {
            color: "#fff",
            font: { weight: "bold", size: 11 },
            formatter: (value, ctx) => {
              let sum = 0;
              let dataArr = ctx.chart.data.datasets[0].data;
              dataArr.map((data) => {
                sum += data;
              });
              if (sum === 0) return "";
              let percentage = ((value * 100) / sum).toFixed(0) + "%";
              return value > 0 ? `${value}\n(${percentage})` : "";
            },
            textAlign: "center",
          },
        },
      },
    });
  }

  const searchInput = document.getElementById("userSearch");
  const tableRows = document.querySelectorAll("#usersTable tbody tr");

  if (searchInput) {
    searchInput.addEventListener("keyup", function () {
      const query = this.value.toUpperCase();
      tableRows.forEach((row) => {
        const userText = row.querySelector(".user-text");
        if (userText) {
          const text = userText.textContent.toUpperCase();
          row.style.display = text.includes(query) ? "" : "none";
        }
      });
    });
  }
});
