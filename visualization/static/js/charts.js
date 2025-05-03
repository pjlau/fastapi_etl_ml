var myChart = echarts.init(document.getElementById("chart"));

fetch("/api/data")
  .then(response => response.json())
  .then(data => {
    const option = {
      title: { text: "Customer Spending" },
      tooltip: {},
      xAxis: { data: data.names },
      yAxis: {},
      series: [{ name: "Total Spent", type: "bar", data: data.total_spent }]
    };
    myChart.setOption(option);
  });