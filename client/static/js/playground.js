// playground.js
import { savePromptAction, saveNamespaceAction, loadPromptContentAction, 
    loadTreeAction, loadModelsAction, getPidAction, sendPromptAction} from './router.js';
import { markedPromise } from './marked-wrapper.js';
// import { marked } from 'https://cdn.jsdelivr.net/npm/marked/marked.esm.js';



document.addEventListener('DOMContentLoaded', function() {
    loadNamespaceTree();
    loadModels();

    const namespace = localStorage.getItem('namespace');
    const filename = localStorage.getItem('filename');
    const version = localStorage.getItem('version');

    if (namespace && filename && version) {
        loadPromptContent(namespace, filename, version);
    }
});

// 添加事件监听器
document.querySelectorAll('[action-data]').forEach(button => {
    // const action = button.getAttribute('action-data')
    // 判断是否select
    if (button.tagName === 'SELECT') {
        button.addEventListener('change', function() {
            const action = this.getAttribute('action-data');
            if (action && typeof actions[action] === 'function') {
                actions[action]();
            }
        });
    } else if (button.tagName === 'INPUT') {
        //监听回车事件
        button.addEventListener('keydown', function(e) {
            if (e.keyCode === 13) {
                const action = this.getAttribute('action-data');
                if (action && typeof actions[action] === 'function') {
                    actions[action]();
                }
            }
        });
    } else {
        button.addEventListener('click', function() {
            const action = this.getAttribute('action-data');
            if (action && typeof actions[action] === 'function') {
                actions[action]();
            }
        });
    }
});

const actions = {
    'createNamespace': createNamespace,
    'createPrompts': createPrompts,
    'savePrompt': savePrompt,
    'changeVersion': changeVersion,
    'sendPrompt': sendPrompt,
    'search': search,
    'createAPI': createAPI,
};


function loadNamespaceTree() {
    loadTreeAction((data) => {
        const namespaceTree = document.getElementById('namespaceTree');
        namespaceTree.innerHTML = ''; // 清空现有的树结构
        buildNamespaceTree(namespaceTree, data.tree);
    });
}

function loadModels() {
    loadModelsAction((data) => {
        const modelsSelect = document.getElementById('models');
        modelsSelect.innerHTML = ''; // 清空现有的选项
        data.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            modelsSelect.appendChild(option);
        });
    });
}

// 创建命名空间树
function buildNamespaceTree(container, treeData) {
    Object.keys(treeData).forEach(namespace => {
        const namespaceNode = document.createElement('div');
        namespaceNode.className = 'namespace-node';
        namespaceNode.id = namespace;

        const nodecount = Array.isArray(treeData[namespace]) ? treeData[namespace].length : 0;
        namespaceNode.textContent = "> "+namespace+" ( "+nodecount+" )";

        const childContainer = document.createElement('ul');
        childContainer.style.display = 'block';

        namespaceNode.addEventListener('click', function() {
            if (childContainer.style.display === 'none') {
                childContainer.style.display = 'block';
            } else {
                childContainer.style.display = 'none';
            }
        });

        container.appendChild(namespaceNode);
        container.appendChild(childContainer);

        treeData[namespace].forEach(file => {
            const fileNode = document.createElement('li');
            fileNode.className = 'file-node';
            fileNode.textContent = file.filename;
            fileNode.addEventListener('click', function() {
                loadPromptContent(namespace, file.filename, file.version)
            });
            childContainer.appendChild(fileNode);
        });
    });
}

// 读取提示词内容和其他信息
function loadPromptContent(namespace, filename, version) {
    loadPromptContentAction(namespace, filename, version, (data) => {
        document.getElementById('promptName').value = data.name;
        document.getElementById('namespaceName').value = data.namespace;
        document.getElementById('systemPrompt').value = data.prompt;
        document.getElementById('userInput').value = data.user_input;
        document.getElementById('models').value = data.model_name;
        document.getElementById('temperature').value = data.temperature ? data.temperature : 1;
        document.getElementById('maxtoken').value = data.max_token ? data.max_token : 4096;
        // 去除:disabled的属性
        document.getElementById('createAPI').disabled = false;
        // 更新版本选择框
        createSelected(data.version, data.versions);
        // 更新本地存储
        localStorage.setItem('namespace', namespace);
        localStorage.setItem('filename', filename);
        localStorage.setItem('version', version);
    });
}

function createSelected(v, vlist) {
    const versionsSelect = document.getElementById('versions');
    versionsSelect.innerHTML = ''; // 清空现有的选项
    vlist.forEach(version => {
        const option = document.createElement('option');
        option.value = version;
        option.textContent = version;
        if (version === v) {
            option.selected = true;
        }
        versionsSelect.appendChild(option);
    });
}

function loadHistoryRecords() {
    // 加载历史对话记录的逻辑
}

 //创建命名空间的逻辑
function createNamespace() {
    const modal = document.createElement('div');
    modal.className = 'modal';

    modal.innerHTML = `
        <div class="modal-content">
            <span class="modal-close">&times;</span>
            <h2 class="title">添加新的空间</h2>
            <div class="form-content">
                <div class="form-group">
                    <label for="namespaceInput">空间名字</label>
                    <input class="default-input w200-px" type="text" id="namespaceInput" placeholder="输入空间名字">
                </div>
            </div>
            <div class="form-button">
                <button class="btn btn-light" id="cancelButton">取消</button>
                <button class="btn btn-primary" id="confirmButton">确认</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    const closeButton = modal.querySelector('.modal-close');
    const cancelButton = modal.querySelector('#cancelButton');
    const confirmButton = modal.querySelector('#confirmButton');

    closeButton.addEventListener('click', () => {
        document.body.removeChild(modal);
    });

    cancelButton.addEventListener('click', () => {
        document.body.removeChild(modal);
    });

    confirmButton.addEventListener('click', () => {
        const namespaceName = document.getElementById('namespaceInput').value;

        saveNamespaceAction(namespaceName, () => {
            document.body.removeChild(modal);
            loadNamespaceTree();
            alert(`创建命名空间: ${namespaceName}`);
        });
    });
}

//创建提示词的逻辑
function createPrompts() {
    const modal = document.createElement('div');
    modal.className = 'modal';

    // 获取命名空间列表
    const namespaceOptions = Array.from(document.querySelectorAll('.namespace-node')).map(node => node.id);

    modal.innerHTML = `
        <div class="modal-content">
            <span class="modal-close">&times;</span>
            <h2 class="title">新建提示词</h2>
            <div class="form-content">
                <div class="form-group">
                    <label for="namespaceSelect">选择空间</label>
                    <select class="default-select" id="namespaceSelect">
                        ${namespaceOptions.map(namespace => `<option value="${namespace}">> ${namespace}</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label for="promptInput">提示词命名</label>
                    <input class="default-input" type="text" id="promptInput" placeholder="输入提示词命名">
                </div>
            </div>
            <div class="form-button">
                <button class="btn btn-secondary" id="cancelButton">取消</button>
                <button class="btn btn-primary" id="confirmButton">确认</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    const closeButton = modal.querySelector('.modal-close');
    const cancelButton = modal.querySelector('#cancelButton');
    const confirmButton = modal.querySelector('#confirmButton');

    closeButton.addEventListener('click', () => {
        document.body.removeChild(modal);
    });

    cancelButton.addEventListener('click', () => {
        document.body.removeChild(modal);
    });

    confirmButton.addEventListener('click', () => {
        const namespaceName = document.getElementById('namespaceSelect').value;
        const promptName = document.getElementById('promptInput').value;
        if (namespaceName && promptName) {
            document.getElementById('namespaceName').value = namespaceName;
            document.getElementById('promptName').value = promptName;
            document.getElementById('versions').innerHTML = ''; // 清空当前版本的select
            document.getElementById('systemPrompt').value = ''; // 清空当前系统提示
            document.getElementById('userInput').value = ''; // 清空当前用户提示
            document.getElementById('historyRecords').value = ''; // 清空历史记录
            document.body.removeChild(modal);
        } else {
            alert('请选择空间并输入提示词命名');
        }
    });

}

// 保存提示词的逻辑
function savePrompt() {
    const namespace = document.getElementById('namespaceName').value
    const name = document.getElementById('promptName').value
    const prompt = document.getElementById('systemPrompt').value
    const model = document.getElementById('models').value
    const userInput = document.getElementById('userInput').value
    const temperature = document.getElementById('temperature').value
    const maxtoken = document.getElementById('maxtoken').value
    savePromptAction(name, namespace, prompt, model, userInput, temperature, maxtoken, (data) => {
        // 更新版本选择框
        createSelected(data.version, data.versions);
        loadNamespaceTree();
        alert('保存提示词成功');
    });
}


// 切换版本的逻辑
function changeVersion() {
    const namespace = document.getElementById('namespaceName').value
    const name = document.getElementById('promptName').value
    const version = document.getElementById('versions').value
    loadPromptContent(namespace, name, version);
}

// 发送提示词的逻辑
function sendPrompt() {
    const namespace = document.getElementById('namespaceName').value
    const name = document.getElementById('promptName').value
    const prompt = document.getElementById('systemPrompt').value
    const model = document.getElementById('models').value
    const userInput = document.getElementById('userInput').value
    const temperature = document.getElementById('temperature').value
    const maxtoken = document.getElementById('maxtoken').value

    createReplyItem({"time":new Date().toLocaleString(), "user":"user", "reply":userInput});
    createReplyItem({"time":new Date().toLocaleString(), "user":model, "reply":"连接中..."});
    setTimeout(() => {
        sendPromptAction(namespace, name, prompt, model, userInput, temperature, maxtoken, (data) => {
            deleteReplyFirstItem();
            createReplyItem(data);
        });
    }, 1000);
    // sendPromptAction(namespace, name, prompt, model, userInput, temperature, maxtoken, (data) => {
    //     deleteReplyFirstItem();
    //     createReplyItem(data);
    // });
}

function deleteReplyFirstItem() {
    const historyRecords = document.getElementById('historyRecords');
    if (historyRecords.children.length > 0) {
        historyRecords.removeChild(historyRecords.children[0]);
    }
}

async function createReplyItem(data) {
    const historyRecords = document.getElementById('historyRecords');
    const replyItem = document.createElement('div');
    replyItem.className = 'reply-item';

    const marked = await markedPromise;

    // 使用 marked.parse 渲染 Markdown 格式的内容
    const replyContent = marked.parse(data.reply);

    replyItem.innerHTML = `
    <div class="reply-item-label">[${data.time}]${data.user}:</div>
    <div class="history-item" style="overflow-wrap: break-word; font-size: 12px; line-height: 15px; margin-top: 0px;">
        ${replyContent}
    </div>
    `;
    historyRecords.insertBefore(replyItem, historyRecords.firstChild);
}

// 搜索提示词的逻辑
function search() {
    const keyword = document.getElementById('search').value
    alert('todo: 搜索提示词成功' + keyword);
}

// 创建API的逻辑
function createAPI() {
    const namespace = document.getElementById('namespaceName').value
    const name = document.getElementById('promptName').value
    getPidAction(namespace, name, (data) => {
        createAPIModal(data.pid);
    });
}

function createAPIModal(pid) {
    const modal = document.createElement('div');
    modal.className = 'modal';

    modal.innerHTML = `
        <div class="modal-content">
            <span class="modal-close">&times;</span>
            <h2 class="title">API</h2>
            <div class="box-bottom-10px">
                <pre class="box-bottom-10px">
<code>POST http://127.0.0.1:5001/apis/llms/v1/`+pid+`
{
    "user_input": "用户输入",
    "params": {}
}</code>
                </pre>
                <p class="font-14px">Tips：当user_input为空的时候会使用模板中保存的用户输入。你可以在这里用占位符来达到不直接使用用户输入作为user_input的目的。</p>
            </div>
            <div class="form-button">
                <button class="btn btn-secondary" id="closeButton">关闭</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    const closeButton = modal.querySelector('.modal-close');
    const closeButtonFooter = modal.querySelector('#closeButton');

    closeButton.addEventListener('click', () => {
        document.body.removeChild(modal);
    });

    closeButtonFooter.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
}