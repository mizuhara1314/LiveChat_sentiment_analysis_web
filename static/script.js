$(document).ready(function () {
    // 获取画布的2D绘图上下文
    var ctx = $("#lineChart")[0].getContext("2d");

    // 初始化Chart.js折线图
    var lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // x轴标签数组，表示时间
            datasets: [{
                label: '負面情绪', // 数据集1标签
                data: [], // 数据集1数据数组
                borderColor: 'red', // 负面情绪折线颜色
                fill: false, // 不填充区域
                cubicInterpolationMode: 'monotone' // 曲线样式
            },
            {
                label: '正面情绪', // 数据集2标签
                data: [], // 数据集2数据数组
                borderColor: 'green', // 正面情绪折线颜色
                fill: false, // 不填充区域
                cubicInterpolationMode: 'monotone' // 曲线样式
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: '時間' // x轴标题
                    }
                },
                y: {
                    beginAtZero: true, // y轴从零开始
                    display: true,
                    title: {
                        display: true,
                        text: '數量' // y轴标题
                    }
                }
            }
        }
    });

    let isPredicting = false; // 标志，避免重复请求

    // 自动化预测的函数
    async function autoPredict() {
        if (isPredicting) {
            console.log('自動化預測已在進行中，請稍等...');
            return;
        }

        isPredicting = true; // 设置为正在请求状态

        try {
            const response = await fetch('/auto_predict', { method: 'POST' });

            if (response.ok) {
                console.log('自動化預測成功');
            } else {
                console.error('自動化預測失败，状态码：', response.status);
            }
        } catch (error) {
            console.error('自動化預測失敗:', error);
        } finally {
            isPredicting = false; // 请求完成后，恢复请求状态
        }
    }

    // 获取最新预测数据的函数
    async function fetchPredictions() {
        try {
            const response = await fetch('/get_predictions');
            const data = await response.json();

            // 保留最新的 50 条数据用于图表
            const recentDataForChart = data.slice(-50);

            // 保留最新的 10 条数据用于列表显示
            const recentDataForList = data.slice(-10);

            // 更新合并列表显示
            $('#combinedList').empty();

            recentDataForList.forEach(item => {
                const time = new Date(item.time);
                const formattedTime = time.toLocaleTimeString('en-GB', { hour12: false });
                const predictionText = item.prediction === 0 ? '負面情绪' : '正面情绪';

                $('#combinedList').prepend(
                    `<li><strong>${predictionText} (${formattedTime}):</strong> ${item.original_data}</li>`
                );
            });

            // 更新图表数据
            const negativeCounts = {};
            const positiveCounts = {};
            const labels = [];

            recentDataForChart.forEach(item => {
                const time = new Date(item.time);
                const formattedTime = time.toLocaleTimeString('en-GB', { hour12: false });

                if (!negativeCounts[formattedTime]) negativeCounts[formattedTime] = 0;
                if (!positiveCounts[formattedTime]) positiveCounts[formattedTime] = 0;

                if (item.prediction == 0) {
                    negativeCounts[formattedTime]++;
                } else if (item.prediction == 1) {
                    positiveCounts[formattedTime]++;
                }

                if (!labels.includes(formattedTime)) {
                    labels.push(formattedTime);
                }
            });

            lineChart.data.labels = labels;
            lineChart.data.datasets[0].data = labels.map(label => negativeCounts[label]);
            lineChart.data.datasets[1].data = labels.map(label => positiveCounts[label]);
            lineChart.update();
        } catch (error) {
            console.error('Error fetching predictions:', error);
        }
    }

    // 定时任务
    setInterval(autoPredict, 5000);
    setInterval(fetchPredictions, 5000);

    // 初次加载数据
    fetchPredictions();
});
