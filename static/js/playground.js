import { savePromptAction, saveNamespaceAction, loadPromptContentAction, loadTreeAction, loadModelsAction} from './router.js';

document.addEventListener('DOMContentLoaded', function() {
    loadNamespaceTree();
    loadModels();
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
    'search': search
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
        // 更新版本选择框
        createSelected(data.version, data.versions);
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
            <span class="close-button">&times;</span>
            <h2 class="box-bottom-20px">添加新的空间</h2>
            <label for="namespaceInput">空间名字</label>
            <input class="default-input w200-px" type="text" id="namespaceInput" placeholder="输入空间名字">
            <div class="modal-actions">
                <button class="btn btn-light" id="cancelButton">取消</button>
                <button class="btn btn-primary" id="confirmButton">确认</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    const closeButton = modal.querySelector('.close-button');
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
            alert(`创建命名空间: ${namespaceName}`);
            document.body.removeChild(modal);
            loadNamespaceTree();
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
            <span class="close-button">&times;</span>
            <h2 class="box-bottom-20px">新建提示词</h2>
            <div class="box-bottom-10px">
                <label for="namespaceSelect">选择空间</label>
                <select class="default-select w200-px" id="namespaceSelect">
                    ${namespaceOptions.map(namespace => `<option value="${namespace}">> ${namespace}</option>`).join('')}
                </select>
            </div>
            <div>
                <label for="promptInput">提示词命名</label>
                <input class="default-input w200-px" type="text" id="promptInput" placeholder="输入提示词命名">
            </div>
            <div class="modal-actions">
                <button class="btn btn-secondary" id="cancelButton">取消</button>
                <button class="btn btn-primary" id="confirmButton">确认</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    const closeButton = modal.querySelector('.close-button');
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
        alert('保存提示词成功');
        // 更新版本选择框
        createSelected(data.version, data.versions);
        loadNamespaceTree();
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
    const prompt = document.getElementById('systemPrompt').value
    const model = document.getElementById('models').value
    const userInput = document.getElementById('userInput').value
    const temperature = document.getElementById('temperature').value
    const maxtoken = document.getElementById('maxtoken').value
    alert('todo: 发送提示词成功');
}

// 搜索提示词的逻辑
function search() {
    const keyword = document.getElementById('search').value
    alert('todo: 搜索提示词成功' + keyword);
}