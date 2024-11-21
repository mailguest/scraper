let currentJobId = null;

// 加载任务列表
async function loadJobs() {
    try {
        const response = await fetch('/apis/jobs');
        const jobs = await response.json();
        const tbody = document.getElementById('jobsTable');
        tbody.innerHTML = '';
        
        jobs.forEach(job => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${job.id}</td>
                <td>${job.name}</td>
                <td>${job.cron}</td>
                <td>
                    <button class="btn ${job.enabled ? 'btn-success' : 'btn-danger'}" 
                            onclick="toggleJob('${job.id}', this)">
                        ${job.enabled ? '已启用' : '已禁用'}
                    </button>
                </td>
                <td>${job.description || ''}</td>
                <td>
                    <button class="btn btn-warning" onclick="editJob('${job.id}')">编辑</button>
                    <button class="btn btn-success" onclick="executeJob('${job.id}')" 
                            ${!job.enabled ? 'disabled' : ''}>执行</button>
                    <button class="btn btn-danger" onclick="deleteJob('${job.id}')">删除</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading jobs:', error);
        alert('加载任务列表失败');
    }
}

// 显示创建任务模态框
function showCreateModal() {
    currentJobId = null;
    document.getElementById('modalTitle').textContent = '创建任务';
    document.getElementById('jobForm').reset();
    document.getElementById('jobModal').style.display = 'block';
}

// 显示编辑任务模态框
async function editJob(jobId) {
    try {
        const response = await fetch(`/apis/jobs/${jobId}`);
        const job = await response.json();
        
        currentJobId = jobId;
        document.getElementById('modalTitle').textContent = '编辑任务';
        document.getElementById('jobId').value = job.id;
        document.getElementById('jobName').value = job.name;
        document.getElementById('jobCron').value = job.cron;
        document.getElementById('jobFunction').value = job.function;
        document.getElementById('jobEnabled').value = job.enabled;
        document.getElementById('jobDescription').value = job.description || '';
        
        document.getElementById('jobModal').style.display = 'block';
    } catch (error) {
        console.error('Error loading job:', error);
        alert('加载任务详情失败');
    }
}

// 关闭模态框
function closeModal() {
    document.getElementById('jobModal').style.display = 'none';
}

// 执行任务
async function executeJob(jobId) {
    if (!confirm('确定要立即执行该任务吗？')) return;
    
    const button = event.target;
    const row = button.closest('tr');
    try {
        setRowButtonsState(row, true);
        button.classList.add('btn-loading');
        
        const response = await fetch(`/apis/jobs/${jobId}/execute`, {
            method: 'POST'
        });
        const result = await response.json();
        alert(result.message || '执行成功');
    } catch (error) {
        console.error('Error executing job:', error);
        alert('执行任务失败');
    } finally {
        button.classList.remove('btn-loading');
        setRowButtonsState(row, false);
    }
}

// 删除任务
async function deleteJob(jobId) {
    if (!confirm('确定要删除该任务吗？')) return;
    
    const button = event.target;
    const row = button.closest('tr');
    try {
        setRowButtonsState(row, true);
        button.classList.add('btn-loading');
        
        await fetch(`/apis/jobs/${jobId}`, {
            method: 'DELETE'
        });
        loadJobs();
    } catch (error) {
        console.error('Error deleting job:', error);
        alert('删除任务失败');
    } finally {
        button.classList.remove('btn-loading');
        setRowButtonsState(row, false);
    }
}

// 表单提交处理
document.getElementById('jobForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const jobData = {
        id: formData.get('id'),
        name: formData.get('name'),
        cron: formData.get('cron'),
        function: formData.get('function'),
        enabled: formData.get('enabled') === 'true',
        description: formData.get('description')
    };

    try {
        const method = currentJobId ? 'PUT' : 'POST';
        const url = currentJobId ? `/apis/jobs/${currentJobId}` : '/apis/jobs';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jobData)
        });

        if (response.ok) {
            closeModal();
            loadJobs();
        } else {
            const error = await response.json();
            alert(error.error || '操作失败');
        }
    } catch (error) {
        console.error('Error saving job:', error);
        alert('保存任务失败');
    }
});

// 初始加载
loadJobs();

// 切换任务状态
async function toggleJob(jobId, button) {
    const row = button.closest('tr');
    try {
        setRowButtonsState(row, true);
        button.classList.add('btn-loading');
        
        const response = await fetch(`/apis/jobs/${jobId}/toggle`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (response.ok) {
            const enabled = result.enabled;
            button.textContent = enabled ? '已启用' : '已禁用';
            button.className = `btn ${enabled ? 'btn-success' : 'btn-danger'}`;
            
            const executeButton = row.querySelector('button[onclick^="executeJob"]');
            executeButton.disabled = !enabled;
            
            alert(result.message);
        } else {
            alert(result.error || '操作失败');
        }
    } catch (error) {
        console.error('Error toggling job:', error);
        alert('切换任务状态失败');
    } finally {
        button.classList.remove('btn-loading');
        setRowButtonsState(row, false);
    }
}

// 添加辅助函数：设置行按钮的禁用状态
function setRowButtonsState(row, disabled) {
    const buttons = row.querySelectorAll('button');
    buttons.forEach(button => {
        button.disabled = disabled;
    });
}