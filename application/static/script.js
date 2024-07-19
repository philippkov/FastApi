// script.js

document.addEventListener('DOMContentLoaded', () => {
    updateUI();
    if (window.location.pathname === '/available') {
        fetchAvailableBooks();
    } else if (window.location.pathname === '/myrequests') {
        fetchRequests();
    } else if (window.location.pathname === '/receivedrequests') {
        fetchReceivedRequests();
    }
});

function updateUI() {
    if (localStorage.getItem('access_token')) {
        document.getElementById('loginItem').style.display = 'none';
        document.getElementById('logoutItem').style.display = 'block';
        document.getElementById('registerItem').style.display = 'none';
        if (document.getElementById('bookTableBody')) {
            fetchBooks();
        }
    } else {
        document.getElementById('loginItem').style.display = 'block';
        document.getElementById('logoutItem').style.display = 'none';
        document.getElementById('registerItem').style.display = 'block';
    }
}

async function fetchAvailableBooks() {
    const tbody = document.getElementById('availableBooksTableBody');
    if (!tbody) return;

    const token = localStorage.getItem('access_token');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

    const response = await fetch('/available/', {
        method: 'GET',
        headers: headers
    });

    if (!response.ok) {
        alert('Failed to fetch available books.');
        return;
    }

    const books = await response.json();
    tbody.innerHTML = '';
    books.forEach((book, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<th scope="row">${index + 1}</th>
                        <td>${book.title}</td>
                        <td>${book.author}</td>
                        <td>${book.owner_id}</td>
                        <td><button class="btn btn-secondary" onclick="requestBook(${book.id})">Запросить книгу</button></td>`;
        tbody.appendChild(tr);
    });
}

async function fetchRequests() {
    const tbody = document.getElementById('requestsTableBody');
    if (!tbody) return;

    const token = localStorage.getItem('access_token');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

    const response = await fetch('/book_requests/', {
        method: 'GET',
        headers: headers
    });

    if (!response.ok) {
        alert('Authentication required. Please log in.');
        window.location.href = '/login';
        return;
    }

    const requests = await response.json();
    tbody.innerHTML = '';
    requests.forEach((request, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<th scope="row">${index + 1}</th>
                        <td>${request.book_id}</td>
                        <td>${new Date(request.request_date).toLocaleString()}</td>
                        <td>${request.status}</td>`;
        tbody.appendChild(tr);
    });
}

async function fetchReceivedRequests() {
    const tbody = document.getElementById('receivedRequestsTableBody');
    if (!tbody) return;

    const token = localStorage.getItem('access_token');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

    const response = await fetch('/book_requests/received/', {
        method: 'GET',
        headers: headers
    });

    if (!response.ok) {
        alert('Failed to fetch received requests.');
        return;
    }

    const requests = await response.json();
    tbody.innerHTML = '';
    requests.forEach((request, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<th scope="row">${index + 1}</th>
                        <td>${request.book_id}</td>
                        <td>${request.requester_id}</td>
                        <td>${new Date(request.request_date).toLocaleString()}</td>
                        <td>${request.status}</td>
                        <td>
                            <button class="btn btn-success" onclick="approveRequest(${request.id})">Подтвердить</button>
                            <button class="btn btn-danger" onclick="rejectRequest(${request.id})">Отклонить</button>
                        </td>`;
        tbody.appendChild(tr);
    });
}

async function register() {
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;

    const response = await fetch('/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username, password: password })
    });

    const data = await response.json();
    if (response.ok) {
        alert(data.message);
        updateUI(true);
    } else {
        alert(`Registration failed: ${data.detail}`);
    }
}

async function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    const response = await fetch('/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    });

    const data = await response.json();
    if (response.ok) {
        localStorage.setItem('access_token', data.access_token);
        updateUI(true);
        window.location.href = '/mybooks';
    } else {
        alert(`Login failed: ${data.detail}`);
    }
}

async function fetchBooks() {
    const tbody = document.getElementById('bookTableBody');
    if (!tbody) return;

    const token = localStorage.getItem('access_token');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

    const response = await fetch('/mybooks/', {
        method: 'GET',
        headers: headers
    });

    if (!response.ok) {
        alert('Authentication required. Please log in.');
        window.location.href = '/login';
        return;
    }

    const books = await response.json();
    tbody.innerHTML = '';
    books.forEach((book, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<th scope="row">${index + 1}</th>
                        <td>${book.title}</td>
                        <td>${book.author}</td>
                        <td>${book.owner.id} - ${book.owner.username}</td>
                        <td>${book.is_available ? 'Да' : 'Нет'}</td>
                        <td>
                            <button class="btn btn-secondary" onclick="toggleAvailability(${book.id}, ${book.is_available})">${book.is_available ? 'Убрать с обмена' : 'Выставить на обмен'}</button>
                            <button class="btn btn-danger" onclick="deleteBook(${book.id})">Удалить</button>
                        </td>`;
        tbody.appendChild(tr);
    });
}

async function addBook() {
    const title = document.getElementById('bookTitle').value;
    const author = document.getElementById('bookAuthor').value;
    const token = localStorage.getItem('access_token');

    const response = await fetch('/books/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ title: title, author: author })
    });

    if (response.ok) {
        alert('Book added successfully!');
        fetchBooks();
    } else {
        const data = await response.json();
        alert(`Failed to add book: ${JSON.stringify(data)}`);
    }
}

async function toggleAvailability(bookId, currentStatus) {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`/books/${bookId}/availability?is_available=${!currentStatus}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });

    if (response.ok) {
        alert('Book availability updated successfully!');
        fetchBooks();
    } else {
        const data = await response.json();
        alert(`Failed to update book availability: ${JSON.stringify(data)}`);
    }
}

async function deleteBook(bookId) {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`/books/${bookId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });

    if (response.ok) {
        alert('Book deleted successfully!');
        fetchBooks();
    } else {
        const data = await response.json();
        alert(`Failed to delete book: ${JSON.stringify(data)}`);
    }
}

async function requestBook(bookId) {
    const token = localStorage.getItem('access_token');

    const response = await fetch('/book_requests/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ book_id: bookId })
    });

    if (response.ok) {
        alert('Запрос на книгу отправлен успешно!');
        fetchAvailableBooks();
    } else {
        const data = await response.json();
        alert(`Failed to request book: ${JSON.stringify(data)}`);
    }
}

async function approveRequest(requestId) {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`/book_requests/${requestId}/approve`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });

    if (response.ok) {
        alert('Запрос на книгу подтвержден.');
        fetchReceivedRequests();
    } else {
        const data = await response.json();
        alert(`Failed to approve request: ${JSON.stringify(data)}`);
    }
}

async function rejectRequest(requestId) {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`/book_requests/${requestId}/reject`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });

    if (response.ok) {
        alert('Запрос на книгу отклонен.');
        fetchReceivedRequests();
    } else {
        const data = await response.json();
        alert(`Failed to reject request: ${JSON.stringify(data)}`);
    }
}

async function logout() {
    localStorage.removeItem('access_token');
    updateUI(false);
    window.location.href = '/login';
}
