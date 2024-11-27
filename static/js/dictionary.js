// FILE: static/js/dictionary.js

//  Load
document.addEventListener('DOMContentLoaded', function() {
    refreshDictionaries();
    setupEnumInputListener();
});

//  Refresh
function refreshDictionaries() {
    fetch('/apis/dictionaries')
        .then(response => response.json())
        .then(data => {
            renderDictionaries(data);
        });
}

//  Render
function renderDictionaries(data) {
    const dictionaryTable = document.getElementById('dictionaryTable');
    dictionaryTable.innerHTML = '';
    if(data.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5" style="text-align: center; padding: 20px;">没有数据</td>';
        dictionaryTable.appendChild(row);
        return;
    }
    
    data.forEach(dictionary => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${dictionary.parent || ''}</td>
            <td>${dictionary.key}</td>
            <td>${dictionary.value}</td>
            <td>${dictionary.description}</td>
            <td>
                <button class="btn btn-warning" onclick="editDictionary('${dictionary._id}')">编辑</button>
                <button class="btn btn-danger" onclick="confirmDeleteDictionary('${dictionary._id}')">删除</button>
            </td>
        `;
        dictionaryTable.appendChild(row);
    });
    document.getElementById('dictionaryCount').innerText = data.length;
}

//  Show Add Modal
function showAddDictionaryModal() {
    document.getElementById('dictionaryForm').reset();
    document.getElementById('dictionaryId').value = '';
    document.getElementById('modalTitle').innerText = '添加字典';
    document.getElementById('dictionaryModal').style.display = 'block';
}

//  Close Modal
function closeDictionaryModal() {
    document.getElementById('dictionaryModal').style.display = 'none';
}

//  Edit
function editDictionary(id) {
    fetch(`/apis/dictionaries/${id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('dictionaryParent').value = data.parent || '';
            document.getElementById('dictionaryId').value = data._id;
            document.getElementById('dictionaryKey').value = data.key;
            document.getElementById('dictionaryValue').value = data.value;
            document.getElementById('dictionaryDescription').value = data.description;
            document.getElementById('modalTitle').innerText = '编辑字典';
            document.getElementById('dictionaryModal').style.display = 'block';
        });
}

//  Delete Confirm
function confirmDeleteDictionary(id) {
    if (confirm('确定要删除这个字典吗？')) {
        deleteDictionary(id);
    }
}

//  Delete
function deleteDictionary(id) {
    fetch(`/apis/dictionaries/${id}`, { method: 'DELETE' })
        .then(() => refreshDictionaries());
}

// Add or Edit
document.getElementById('dictionaryForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const parent = document.getElementById('dictionaryParent').value;
    const id = document.getElementById('dictionaryId').value;
    const key = document.getElementById('dictionaryKey').value;
    const value = document.getElementById('dictionaryValue').value;
    const description = document.getElementById('dictionaryDescription').value;

    const method = id ? 'PUT' : 'POST';
    const url = id ? `/apis/dictionaries/${id}` : '/apis/dictionaries';

    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parent, key, value, description })
    }).then(() => {
        closeDictionaryModal();
        refreshDictionaries();
    });
});

//  Enum
function setupEnumInputListener() {
    const keyInput = document.getElementById('dictionaryKey');
    keyInput.addEventListener('blur', function() {
        const parentInput = document.getElementById('dictionaryParent');
        if (!parentInput.value) {
            parentInput.value = keyInput.value;
        }
    });
}

// Search
function searchDictionaries() {
    const searchParent = document.getElementById('searchParent').value.trim();
    const searchKey = document.getElementById('searchKey').value.trim();

    fetch('/apis/dictionaries')
        .then(response => response.json())
        .then(data => {
            const filteredData = data.filter(dictionary => {
                return (searchParent === '' || dictionary.parent.includes(searchParent)) &&
                       (searchKey === '' || dictionary.key.includes(searchKey));
            });
            renderDictionaries(filteredData);
        });
}