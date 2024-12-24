

// 登出函数
function logout() {
    if (confirm('确定要退出登录吗？')) {
        // 这里添加登出逻辑
        window.location.href = '/login';
    }
}

// 全局变量，用于存储 toast 队列
const toastQueue = [];
let isProcessingToast = false;

/**
 * 显示提示信息
 * @param {string} type - 提示类型：'success' 或 'error'
 * @param {string} message - 提示信息
 */
function showToast(type, message) {
    // 将新的 toast 添加到队列
    toastQueue.push({ type, message });
    
    // 如果没有正在处理的 toast，开始处理队列
    if (!isProcessingToast) {
        processToastQueue();
    }
}

/**
 * 处理 toast 队列
 */
function processToastQueue() {
    if (toastQueue.length === 0) {
        isProcessingToast = false;
        return;
    }

    isProcessingToast = true;
    const { type, message } = toastQueue.shift();

    // 创建 toast 元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // 计算位置
    const existingToasts = document.querySelectorAll('.toast');
    const offset = existingToasts.length * 60; // 每个 toast 的间距
    
    // 添加到页面
    document.body.appendChild(toast);
    
    // 显示动画
    setTimeout(() => {
        toast.style.opacity = '1';
    }, 100);
    
    // 3秒后移除
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(toast);
            // 处理队列中的下一个 toast
            processToastQueue();
        }, 300);
    }, 3000);
}

// 等待 DOM 完全加载后再执行
document.addEventListener('DOMContentLoaded', function() {
    setInterval(updateOnlineTime, 1000);
    toggleSidebar();
}); 

// 更新在线时长
function updateOnlineTime() {
    try{
        const onlineTimeElement = document.getElementById('onlineTime');
        
        // 检查元素是否存在
        if (!onlineTimeElement) {
            console.error('找不到显示在线时长的元素');
            return;
        }
        
        // 获取或设置登录时间
        let loginTimestamp = localStorage.getItem('loginTimestamp');
        if (!loginTimestamp) {
            loginTimestamp = new Date().getTime();
            localStorage.setItem('loginTimestamp', loginTimestamp);
        } else {
            loginTimestamp = parseInt(loginTimestamp, 10);
        }

        const now = new Date().getTime();
        const diffInSeconds = Math.floor((now - loginTimestamp) / 1000);
        
        // 计算时、分、秒
        const hours = Math.floor(diffInSeconds / 3600);
        const minutes = Math.floor((diffInSeconds % 3600) / 60);
        const seconds = diffInSeconds % 60;
        
        // 格式化时间，保证两位数显示
        const formatNumber = (num) => num.toString().padStart(2, '0');
        const timeString = `${formatNumber(hours)}:${formatNumber(minutes)}:${formatNumber(seconds)}`;
        
        onlineTimeElement.textContent = timeString;
    } catch (error) {
        console.error('更新在线时长时出错:', error);
    }
}

// 侧边栏的缩放
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleButton = document.getElementById('toggle-button');

    // 检查本地存储中是否有 collapsed 状态
    const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
    if (isCollapsed) {
        sidebar.classList.add('collapsed');
        toggleButton.innerHTML = '&raquo;';
    } else {
        toggleButton.innerHTML = '&laquo;';
    }

    toggleButton.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        const isCollapsed = sidebar.classList.contains('collapsed');
        this.innerHTML = isCollapsed ? '&raquo;' : '&laquo;';
        // 将 collapsed 状态保存到本地存储
        localStorage.setItem('sidebar-collapsed', isCollapsed);
    });
}