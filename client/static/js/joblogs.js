let currentPage = 1;
let totalPages = 1;
const pageSize = 10;

document.addEventListener('DOMContentLoaded', function() {
    loadLogs();
});

function getLogs(taskName, status, page, size, callback) {
    fetch(`/apis/jobs/logs?page=${page}&size=${size}${taskName ? '&taskName=' + taskName : ''}${status ? '&status=' + status : ''}`)
    .then(response => response.json())
    .then(data => {callback(data);})
    .catch(error => {
        console.error('Error loading logs:', error);
        showToast('error', '加载列表失败：' + error.message);
    });
}

function renderLogs(data) {
    const logsTable = document.getElementById('logsTable');
    // 检查数据是否为空
    if (!data.items || data.items.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="6" style="text-align: center; padding: 20px;">暂无数据</td>`;
        logsTable.appendChild(row);
        totalPages = 1;
    } else {
        logsTable.innerHTML = '';
        data.items.forEach(log => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${log.task_name}</td>
                <td>${new Date(log.start_time).toLocaleString()}</td>
                <td>${new Date(log.end_time).toLocaleString()}</td>
                <td>${log.status}</td>
                <td>${log.data_count}</td>
                <td>${log.duration}</td>
            `;
            logsTable.appendChild(row);
        });
        totalPages = data.total_pages;
    }
    updatePagination();
}

function loadLogs() {
    const taskName = document.getElementById('searchTaskName').value;
    const status = document.getElementById('searchStatus').value;

    // 模拟获取数据
    getLogs(taskName, status, currentPage, pageSize, function(data) {
        renderLogs(data);
    });
}

function searchLogs() {
    loadLogs();
}

function changePage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    loadLogs(currentPage);
}

function updatePagination() {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    // 如果总页数为1，清空分页并推出
    if (totalPages <= 1) {
        return;
    }
    // 添加"上一页"按钮
    if (currentPage > 1) {
        pagination.innerHTML += `
            <button onclick="changePage(${currentPage - 1})" class="btn btn-light">上一页</button>
        `;
    }

    // 页码显示逻辑
    if (totalPages <= 6) {
        // 总页数不超过6页时，显示所有页码
        for (let i = 1; i <= totalPages; i++) {
            pagination.innerHTML += `
                <button onclick="changePage(${i})" 
                        class="btn ${currentPage === i ? 'btn-primary' : 'btn-light'}">${i}</button>
            `;
        }
    } else {
        // 当总页数大于6页时的显示逻辑
        let startPage, endPage;
        
        if (currentPage <= 3) {
            // 当前页靠近开始
            startPage = 1;
            endPage = 5;
            
            // 显示页码
            for (let i = startPage; i <= endPage; i++) {
                pagination.innerHTML += `
                    <button onclick="changePage(${i})" 
                            class="btn ${currentPage === i ? 'btn-primary' : 'btn-light'}">${i}</button>
                `;
            }
            
            pagination.innerHTML += `<span class="pagination-ellipsis">...</span>`;
            pagination.innerHTML += `
                <button onclick="changePage(${totalPages})" 
                        class="btn ${currentPage === totalPages ? 'btn-primary' : 'btn-light'}">${totalPages}</button>
            `;
            
        } else if (currentPage >= totalPages - 2) {
            // 当前页靠近结束
            startPage = totalPages - 4;
            endPage = totalPages;
            
            pagination.innerHTML += `
                <button onclick="changePage(1)" 
                        class="btn ${currentPage === 1 ? 'btn-primary' : 'btn-light'}">1</button>
            `;
            pagination.innerHTML += `<span class="pagination-ellipsis">...</span>`;
            
            for (let i = startPage; i <= endPage; i++) {
                pagination.innerHTML += `
                    <button onclick="changePage(${i})" 
                            class="btn ${currentPage === i ? 'btn-primary' : 'btn-light'}">${i}</button>
                `;
            }
            
        } else {
            // 当前页在中间
            startPage = currentPage - 2;
            endPage = currentPage + 2;
            
            pagination.innerHTML += `
                <button onclick="changePage(1)" 
                        class="btn ${currentPage === 1 ? 'btn-primary' : 'btn-light'}">1</button>
            `;
            pagination.innerHTML += `<span class="pagination-ellipsis">...</span>`;
            
            for (let i = startPage; i <= endPage; i++) {
                pagination.innerHTML += `
                    <button onclick="changePage(${i})" 
                            class="btn ${currentPage === i ? 'btn-primary' : 'btn-light'}">${i}</button>
                `;
            }
            
            pagination.innerHTML += `<span class="pagination-ellipsis">...</span>`;
            pagination.innerHTML += `
                <button onclick="changePage(${totalPages})" 
                        class="btn ${currentPage === totalPages ? 'btn-primary' : 'btn-light'}">${totalPages}</button>
            `;
        }
    }

    // 添加"下一页"按钮
    if (currentPage < totalPages) {
        pagination.innerHTML += `
            <button onclick="changePage(${currentPage + 1})" class="btn btn-light">下一页</button>
        `;
    }
}

