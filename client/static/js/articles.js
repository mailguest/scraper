let currentPage = 1;
let totalPages = 1;

function loadArticles() {
    const date = document.getElementById('dateFilter').value;
    const source = document.getElementById('source').value;
    const status = document.getElementById('status').value;
    const limit = parseInt(document.getElementById('pageSize').value);
    
    fetch(`/apis/articles?page=${currentPage}&limit=${limit}${date ? '&date=' + date : ''}${source ? '&source=' + source : ''}${status ? '&status=' + status : ''}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('articlesTable');
            tbody.innerHTML = '';

            // 检查数据是否为空
            if (!data.items || data.items.length === 0) {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td colspan="5" style="text-align: center; padding: 20px;">
                        暂无文章数据
                    </td>
                `;
                tbody.appendChild(row);
                totalPages = 1;
            } else {
                data.items.forEach(article => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="article-title-cell" title="${article.title}">
                            <div class="article-title-text">${article.title}</div>
                        </td>
                        <td>${article.date}</td>
                        <td>${article.source}</td>
                        <td>${article.status}</td>
                        <td class="action-column">
                            <button class="btn btn-info" onclick="event.stopPropagation()">
                                查看
                            </button>
                            <button class="btn btn-danger" onclick="event.stopPropagation()">
                                删除
                            </button>
                        </td>
                    `;
                    
                    // 为整行添加点击事件
                    row.addEventListener('click', () => viewArticle(article.UUID));
                    
                    // 为查看按钮添加点击事件
                    const viewButton = row.querySelector('.btn-info');
                    viewButton.addEventListener('click', (e) => {
                        e.stopPropagation();
                        viewArticle(article.UUID);
                    });
                    
                    // 为删除按钮添加点击事件
                    const deleteButton = row.querySelector('.btn-danger');
                    deleteButton.addEventListener('click', (e) => {
                        e.stopPropagation();
                        if (confirm('确定要删除这篇文章吗？')) {
                            deleteArticle(article.UUID);
                        }
                    });
                    
                    tbody.appendChild(row);
                });
                totalPages = data.total_pages;
                
            }
            // 更新分页
            updatePagination();
        })
        .catch(
            error => {
                showToast('error', '加载文章列表失败：' + error.message);
        });
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

function changePage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    loadArticles(currentPage);
}

function viewArticle(uuid) {
    fetch(`/apis/article/${uuid}`)
        .then(response => response.json())
        .then(article => {
            const modal = document.getElementById('articleModal');
            document.getElementById('articleContent').innerHTML = `
                <div class="article-container">
                    <div class="article-header">
                        <h3 class="article-title">${article.title}</h3>
                        <p class="article-meta">
                            发布日期：${article.date || 'undefined'} | 
                            来源：${article.source}
                        </p>
                    </div>
                    <div class="article-body">${article.content}</div>
                </div>
            `;
            modal.style.display = "block";
        })
        .catch(error => showToast('error', '加载文章详情失败：' + error.message));
}

function closeArticleModal() {
    const modal = document.getElementById('articleModal');
    modal.style.display = "none";
    
    // 恢复背景滚动
    document.body.style.overflow = 'auto';
}

function deleteArticle(uuid) {
    fetch(`/apis/article/${uuid}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        showToast('success', '文章已删除');
        loadArticles(); // 重新加载文章列表
    })
    .catch(error => showToast('error', '删除文章失败：' + error.message));
}

// 页面加载和模态框事件处理
document.addEventListener('DOMContentLoaded', () => {
    loadArticles();
    
    // 点击模态框外部关闭
    window.onclick = function(event) {
        const modal = document.getElementById('articleModal');
        if (event.target == modal) {
            closeArticleModal();
        }
    }
}); 