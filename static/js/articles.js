let currentPage = 1;
let totalPages = 1;

function loadArticles() {
    const date = document.getElementById('dateFilter').value;
    const limit = document.getElementById('pageSize').value;
    
    fetch(`/apis/articles?page=${currentPage}&limit=${limit}${date ? '&date=' + date : ''}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('articlesTable');
            tbody.innerHTML = '';
            
            data.items.forEach(article => {
                const row = `
                    <tr>
                        <td>${article.title}</td>
                        <td>${article.publish_date}</td>
                        <td>${article.source}</td>
                        <td>
                            <button class="btn btn-sm btn-info" onclick="viewArticle('${article.uuid}')">
                                <i class="fas fa-eye"></i> 查看
                            </button>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });

            totalPages = Math.ceil(data.total / limit);
            updatePagination();
        })
        .catch(error => showToast('错误', '加载文章列表失败：' + error.message));
}

function updatePagination() {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    if (currentPage > 1) {
        pagination.innerHTML += `
            <button onclick="changePage(${currentPage - 1})" class="btn btn-secondary">上一页</button>
        `;
    }

    for (let i = 1; i <= totalPages; i++) {
        pagination.innerHTML += `
            <button onclick="changePage(${i})" 
                    class="btn ${currentPage === i ? 'btn-primary' : 'btn-secondary'}">${i}</button>
        `;
    }

    if (currentPage < totalPages) {
        pagination.innerHTML += `
            <button onclick="changePage(${currentPage + 1})" class="btn btn-secondary">下一页</button>
        `;
    }
}

function changePage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    loadArticles();
}

function viewArticle(uuid) {
    fetch(`/apis/article/${uuid}`)
        .then(response => response.json())
        .then(article => {
            const modal = document.getElementById('articleModal');
            document.getElementById('articleContent').innerHTML = `
                <h3>${article.title}</h3>
                <p class="article-meta">
                    发布日期：${article.publish_date} | 
                    来源：${article.source}
                </p>
                <div class="article-body">${article.content}</div>
            `;
            modal.style.display = "block";
        })
        .catch(error => showToast('错误', '加载文章详情失败：' + error.message));
}

function closeArticleModal() {
    const modal = document.getElementById('articleModal');
    modal.style.display = "none";
}

function refreshCache() {
    fetch('/apis/refresh', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showToast('成功', '缓存已刷新');
            loadArticles();
        })
        .catch(error => showToast('错误', '刷新缓存失败：' + error.message));
}

function startScrape() {
    fetch('/apis/scrape', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showToast('成功', '爬取任务已启动');
            setTimeout(loadArticles, 3000);
        })
        .catch(error => showToast('错误', '启动爬取失败：' + error.message));
}

// 页面加载和模态框事件处理
document.addEventListener('DOMContentLoaded', () => {
    loadArticles();
    
    // 点击模态框外部关闭
    window.onclick = function(event) {
        const modal = document.getElementById('articleModal');
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}); 