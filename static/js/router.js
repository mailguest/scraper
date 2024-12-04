// 通用的 fetch 方法
async function fetchApi(url, method, body, successcallback, errorCallback) {
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: body ? JSON.stringify(body) : null
        });
        const data = await response.json();
        if (data.error) {
            if (errorCallback) {
                errorCallback(data);
            } else {
                alert('Error: ' + data.error);
            }
        } else {
            if (successcallback) {
                successcallback(data);
            }
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// 路由：保存命名空间
export function saveNamespaceAction(namespace, callback) {
    fetchApi(
        '/apis/prompts/nsave',
        'POST',
        {
            namespace: namespace
        },
        callback
    );
}

// 路由：保存提示词
export function savePromptAction(name, namespace, prompt, model, userInput, temperature, maxtoken, callback) {
    fetchApi(
        '/apis/prompts/save',
        'POST',
        {
            name: name,
            namespace: namespace,
            prompt: prompt,
            model_name: model, 
            user_input: userInput, 
            temperature: temperature, 
            maxtoken: maxtoken,
        },
        callback
    );
}

// 路由: 加载提示词
export function loadPromptContentAction(namespace, name, version, callback) {
    fetchApi(
        '/apis/prompts/get',
        'POST',
        {
            name: name,
            namespace: namespace,
            ...(version && { version: version })
        },
        callback
    );
}

// 路由：加载命名空间树
export function loadTreeAction(callback) {
    fetchApi(
        '/apis/prompts/tree',
        'GET',
        null,
        callback
    );
}

// 路由：加载模型
export function loadModelsAction(callback) {
    fetchApi(
        '/apis/llms/models',
        'GET',
        null,
        callback
    );
}

// 路由：加载文章pid
export function getPidAction(namespace, name, callback) {
    fetchApi(
        '/apis/prompts/pid',
        'POST',
        {
            namespace: namespace,
            name: name
        },
        callback
    );
}

export function sendPromptAction(namespace, name, prompt, model, userInput, temperature, maxtoken, callback) {
    // const data = {};
    // data["reply"] = `{"judge":"PASS"}`;
    // data["time"] = new Date().toLocaleString();
    // data["user"] = model;
    // callback(data);
    // return 
    fetchApi(
        '/apis/llms/chat',
        'POST',
        {
            namespace: namespace,
            name: name,
            prompt: prompt,
            user_input: userInput, 
            model_name: model, 
            temperature: temperature, 
            maxtoken: maxtoken,
        },
        callback
    );
}