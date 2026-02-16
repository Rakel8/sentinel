function buatGrafik(idCanvas, label, warna) {
  const ctx = document.getElementById(idCanvas).getContext("2d");
  return new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: label,
          data: [],
          borderColor: warna,
          backgroundColor: warna + "33",
          borderWidth: 2,
          tension: 0,
          pointRadius: 0,
          fill: true,
        },
      ],
    },
    options: {
      animation: false,
      scales: {
        y: { min: 0, max: 100, grid: { color: "#333" } },
        x: { display: false },
      },
      plugins: { legend: { display: false } },
    },
  });
}

const chartCPU = buatGrafik("cpuChart", "CPU %", "#00ff00");
const chartRAM = buatGrafik("ramChart", "RAM %", "#00ffff");
const chartBAT = buatGrafik("batChart", "Battery %", "#ffaa00");

function updateSatuGrafik(chart, labelWaktu, dataString) {
  let nilai = parseFloat(dataString);

  chart.data.labels.push(labelWaktu);
  chart.data.datasets[0].data.push(nilai);

  if (chart.data.labels.length > 30) {
    chart.data.labels.shift();
    chart.data.datasets[0].data.shift();
  }
  chart.update();
}

async function muatSejarah() {
  try {
    const response = await fetch("/api/history");
    const dataSejarah = await response.json();

    dataSejarah.forEach((item) => {
      chartCPU.data.labels.push(item.waktu);
      chartCPU.data.datasets[0].data.push(item.cpu);

      chartRAM.data.labels.push(item.waktu);
      chartRAM.data.datasets[0].data.push(item.ram);

      chartBAT.data.labels.push(item.waktu);
      chartBAT.data.datasets[0].data.push(item.baterai);
    });

    chartCPU.update();
    chartRAM.update();
    chartBAT.update();
    console.log("✅ Sejarah berhasil dimuat dari Database!");
  } catch (error) {
    console.error("Gagal memuat sejarah:", error);
  }
}

async function updateDashboard() {
  try {
    let waktu = new Date().toLocaleTimeString();

    let resCpu = await fetch("/monitor/cpu");
    let jsonCpu = await resCpu.json();
    updateSatuGrafik(chartCPU, waktu, jsonCpu.CPU);

    let resRam = await fetch("/monitor/ram");
    let jsonRam = await resRam.json();
    updateSatuGrafik(chartRAM, waktu, jsonRam.RAM);

    let resBat = await fetch("/monitor/battery");
    let jsonBat = await resBat.json();
    updateSatuGrafik(chartBAT, waktu, jsonBat.Battery);
  } catch (err) {
    console.log("Error fetch data:", err);
  }
}

async function tidurkanLaptop() {
  if (confirm("Yakin mau tidur?")) {
    alert("Goodnight! 💤");
    fetch("/action/sleep").catch((e) => console.log("Offline."));
  }
}

async function matikanLaptop() {
  if (confirm("Yakin mau shutdown?")) {
    alert("Goodbye!");
    fetch("/action/shutdown").catch((e) => console.log("Shutdown"));
  }
}

muatSejarah().then(() => {
  setInterval(updateDashboard, 1000);
});
