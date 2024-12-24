// 设置按钮加载状态
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.classList.add('btn-loading');
        // 保存原始文本
        button.dataset.originalText = button.textContent;
        button.textContent = '';
    } else {
        button.disabled = false;
        button.classList.remove('btn-loading');
        // 恢复原始文本
        button.textContent = button.dataset.originalText;
        delete button.dataset.originalText;
    }
}

// 加载代理列表
async function loadProxies() {
    try {
        const response = await fetch('/apis/proxies');
        const data = await response.json();
        
        // 确保数据是数组
        const proxies = Array.isArray(data) ? data : [];
        
        const proxyTable = document.getElementById('proxyTable');
        proxyTable.innerHTML = '';
        
        if (proxies.length === 0) {
            // 如果没有数据，显示提示信息
            proxyTable.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 20px;">
                        暂无代理数据
                    </td>
                </tr>
            `;
        } else {
            proxies.forEach(proxy => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${proxy.ip || '-'}</td>
                    <td>${proxy.port || '-'}</td>
                    <td>${proxy.area || '-'}</td>
                    <td>${proxy.period_of_validity || '-'}</td>
                    <td>
                        <span class="status-badge ${proxy.status === 1 ? 'status-valid' : 'status-invalid'}">
                            ${proxy.status === 1 ? '可用' : '不可用'}
                        </span>
                    </td>
                    <td>
                        ${generateButtonHtml(proxy.ip, proxy.port)}
                    </td>
                `;
                proxyTable.appendChild(row);
            });
        }
        
        // 更新代理数量
        document.getElementById('proxyCount').textContent = proxies.length;
        
    } catch (error) {
        console.error('Error loading proxies:', error);
        // 显示错误信息
        const proxyTable = document.getElementById('proxyTable');
        proxyTable.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 20px; color: #dc3545;">
                    加载失败：${error.message}
                </td>
            </tr>
        `;
        document.getElementById('proxyCount').textContent = '0';
    }
}

// 刷新代理列表
async function refreshProxies() {
    const refreshBtn = document.querySelector('.toolbar .btn-primary');
    try {
        setButtonLoading(refreshBtn, true);
        
        const response = await fetch('/apis/proxies/refresh', {
            method: 'POST'
        });
        const result = await response.json();
        
        if (response.ok) {
            await loadProxies();
            alert('代理列表已刷新');
        } else {
            alert(result.error || '刷新代理列表失败');
        }
    } catch (error) {
        console.error('Error refreshing proxies:', error);
        alert('刷新代理列表失败');
    } finally {
        setButtonLoading(refreshBtn, false);
    }
}

// 测试代理
async function testProxy(ip, port) {
    const testBtn = event.target;  // 获取触发事件的按钮
    try {
        setButtonLoading(testBtn, true);
        
        const response = await fetch(`/apis/proxies/${encodeURIComponent(ip + ':' + port)}/test`, {
            method: 'POST'
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
        } else {
            await loadProxies();
            alert(result.error || '测试代理失败');
        }
    } catch (error) {
        console.error('Error testing proxy:', error);
        alert('测试代理失败');
    } finally {
        setButtonLoading(testBtn, false);
    }
}

// 删除代理
async function deleteProxy(ip, port) {
    if (!confirm('确定要删除该代理吗？')) return;
    
    const deleteBtn = event.target;  // 获取触发事件的按钮
    try {
        setButtonLoading(deleteBtn, true);
        
        const response = await fetch(`/apis/proxies/${encodeURIComponent(ip + ':' + port)}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadProxies();
            alert('代理已删除');
        } else {
            const result = await response.json();
            alert(result.error || '删除代理失败');
        }
    } catch (error) {
        console.error('Error deleting proxy:', error);
        alert('删除代理失败');
    } finally {
        setButtonLoading(deleteBtn, false);
    }
}

// 修改生成按钮的HTML，添加事件参数
function generateButtonHtml(ip, port) {
    return `
        <button class="btn btn-primary" onclick="testProxy('${ip}', '${port}', event)">测试</button>
        <button class="btn btn-danger" onclick="deleteProxy('${ip}', '${port}', event)">删除</button>
    `;
}

// 页面加载时加载代理列表
document.addEventListener('DOMContentLoaded', loadProxies); 