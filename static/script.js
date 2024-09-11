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

    // 自动化预测的函数
    async function autoPredict() {
        try {
            await fetch('/auto_predict', { method: 'POST' });
            console.log('自動化預測成功');
        } catch (error) {
            console.error('自動化預測失敗:', error);
        }
    }

    // 获取最新预测数据的函数
    async function fetchPredictions() {
        try {
            const response = await fetch('/get_predictions');
            const data = await response.json();

            // 仅保留最新的10条预测
            const recentData = data.slice(-10);

            // 清空合并后的列表
            $('#combinedList').empty();

            // 更新图表数据
            const negativeCounts = {};
            const positiveCounts = {};
            const labels = [];

            recentData.forEach(item => {
                const time = new Date(item.time);  // 转换时间字符串为日期对象
                const formattedTime = time.toLocaleTimeString('en-GB', { hour12: false }); // 格式化时间为 "HH:mm:ss"

                // 将预测结果和原始数据合并显示
                const predictionText = item.prediction === 0 ? '負面情绪' : '正面情绪';
                $('#combinedList').prepend(`<li><strong>${predictionText} (${formattedTime}):</strong> ${item.original_data}</li>`);

                // 初始化数据计数
                if (!negativeCounts[formattedTime]) negativeCounts[formattedTime] = 0;
                if (!positiveCounts[formattedTime]) positiveCounts[formattedTime] = 0;

                // 统计正负情绪数量
                if (item.prediction == 0) { // 负面情绪
                    negativeCounts[formattedTime]++;
                } else if (item.prediction == 1) { // 正面情绪
                    positiveCounts[formattedTime]++;
                }

                // 添加时间标签（避免重复添加）
                if (!labels.includes(formattedTime)) {
                    labels.push(formattedTime);
                }
            });

            // 更新Chart.js数据
            lineChart.data.labels = labels; // 更新x轴标签

            // 处理负面和正面数据集
            lineChart.data.datasets[0].data = labels.map(label => negativeCounts[label]); // 负面情绪数量
            lineChart.data.datasets[1].data = labels.map(label => positiveCounts[label]); // 正面情绪数量

            lineChart.update(); // 更新图表
        } catch (error) {
            console.error('Error fetching predictions:', error);
        }
    }

    // 每5秒调用一次自动化预测
    setInterval(autoPredict, 5000);

    // 每5秒调用一次获取最新预测数据的函数
    setInterval(fetchPredictions, 5000);

    // 初次加载数据
    fetchPredictions();
});
