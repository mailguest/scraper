let currentPage = 1;
const pageSize = 10;

document.addEventListener('DOMContentLoaded', function() {
    loadLogs();
});

function loadLogs() {
    const taskName = document.getElementById('searchTaskName').value;
    const status = document.getElementById('searchStatus').value;

    // 模拟获取数据
    const logs = getLogs(taskName, status, currentPage, pageSize);

    const logsTable = document.getElementById('logsTable');
    logsTable.innerHTML = '';

    logs.forEach(log => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${log.task_name}</td>
            <td>${new Date(log.start_time.$date).toLocaleString()}</td>
            <td>${new Date(log.end_time.$date).toLocaleString()}</td>
            <td>${log.status}</td>
            <td>${log.data_count}</td>
            <td>${log.duration.toFixed(3)}</td>
        `;
        logsTable.appendChild(row);
    });

    updatePagination();
}

function searchLogs() {
    currentPage = 1;
    loadLogs();
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        loadLogs();
    }
}

function nextPage() {
    currentPage++;
    loadLogs();
}

function updatePagination() {
    const pageInfo = document.getElementById('pageInfo');
    pageInfo.textContent = `第 ${currentPage} 页`;
}

function getLogs(taskName, status, page, size) {
    // 模拟数据
    const allLogs = [
        {
            "task_name": "content_scraper",
            "start_time": { "$date": "2024-11-27T23:15:00.005Z" },
            "status": "completed",
            "data_count": 0,
            "duration": 0.014383,
            "end_time": { "$date": "2024-11-27T23:15:00.019Z" }
        },
        // 添加更多模拟数据
    ];

    // 过滤数据
    let filteredLogs = allLogs;
    if (taskName) {
        filteredLogs = filteredLogs.filter(log => log.task_name.includes(taskName));
    }
    if (status) {
        filteredLogs = filteredLogs.filter(log => log.status === status);
    }

    // 分页
    const start = (page - 1) * size;
    const end = start + size;
    return filteredLogs.slice(start, end);
}