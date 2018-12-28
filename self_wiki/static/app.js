var SELF_WIKI = {};

function sendFile() {
    const input = document.getElementById('file-input');
    const formData = new FormData();
    for (let i = 0; i < input.files.length; i++) {
        formData.append('file', input.files[i], input.files[i].filename);
    }
    const xhr = new XMLHttpRequest();
    xhr.open('POST', window.location.toString() + '/upload');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 201) {
            console.log("files sent");
        }
    };
    xhr.send(formData);
}

Mousetrap.bind('ctrl+c n', function (e) {
    let text = prompt('', 'todo text');
    if (text !== '') {
        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 201) {
                console.log(`${text} created`);
            }
        };
        xhr.open('post', '/todo');
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify({'text': text, 'done': false}));
    }
    getTodoList();
});

Mousetrap.bind('ctrl+c d', function (e) {
    if (confirm('Really delete this page?')) {
        let xhr = new XMLHttpRequest();
        xhr.onload = function() {
            window.location.pathname = '/'
        };
        xhr.open('delete', window.location.toString());
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send();
    }
});

function delTodo(id) {
    let xhr = new XMLHttpRequest();
    xhr.open('delete', '/todo');
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify({'id': id}));
    document.getElementById('todo_' + id).parentElement.remove();
}

function toggleTodoDone(id) {
    let todo = document.getElementById("todo_" + id);
    if (todo.className === "notdone")
        todo.className = 'done';
    else
        todo.className = 'notdone';
    let xhr = new XMLHttpRequest();
    xhr.open('put', '/todo');
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify({'id': id, 'done': todo.className === "done"}));
}

function getTodoList() {
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            let list = document.getElementById('todoList');
            list.innerHTML = '';
            JSON.parse(xhr.responseText).forEach(function (todo) {
                list.innerHTML += `<li><button class="button" onclick="delTodo(${todo.id})">del</button>
<span id="todo_${todo.id}" class="${todo.done ? 'done' : 'notdone'}" onclick="toggleTodoDone(${todo.id})">${todo.text}</span></li>`;
            });
        }
    };
    xhr.open('get', '/todo');
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send();
}

function saveCurrentPage(editor) {
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 201) {
            console.log("Saved current page");
        }
    };
    xhr.open('put', window.location.toString() + '/save');
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify({'markdown': editor.value()}));
}

function setPageList(datalist) {
    let xhr = new XMLHttpRequest();
    xhr.onload = function () {
        datalist.innerHTML = '';
        JSON.parse(xhr.responseText).forEach(function (data) {
            let option = document.createElement('option');
            option.value = data.path.slice(0, -3);
            datalist.appendChild(option);
        });
    };
    xhr.open('get', '/search');
    xhr.send();

}

function init() {
    // generate accesskeys
    keykeeper();
    // get todolist, then set periodicity
    getTodoList();
    SELF_WIKI.todoThread = setInterval(getTodoList, 10000);
}