// 记录登录时间
const loginTimestamp = new Date().getTime();

// 更新在线时长
function updateOnlineTime() {
    const onlineTimeElement = document.getElementById('onlineTime');
    
    // 检查元素是否存在
    if (!onlineTimeElement) {
        console.error('找不到显示在线时长的元素');
        return;
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
}

// 登出函数
function logout() {
    if (confirm('确定要退出登录吗？')) {
        // 这里添加登出逻辑
        window.location.href = '/login';
    }
}

// 等待 DOM 完全加载后再执行
document.addEventListener('DOMContentLoaded', function() {
    try {
        // 检查元素是否存在
        const onlineTimeElement = document.getElementById('onlineTime');
        if (!onlineTimeElement) {
            console.error('找不到显示在线时长的元素');
            return;
        }
        
        // 立即更新一次
        updateOnlineTime();
        // 每秒更新一次时间
        setInterval(updateOnlineTime, 1000);
    } catch (error) {
        console.error('初始化在线时长显示时出错:', error);
    }
}); 