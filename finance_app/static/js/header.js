// All functions that need to be loaded with header

//const csrfToken = "{{ csrf_token }}";

function markAllUnread() {
  var csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value; 

  fetch('/mark-all-unread/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/json',
    },
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      alert("Všechny notifikace se Vám znovu zobrazí po obnovení stránky");
    } else {
      console.error(data.message);
    }
  })
  .catch(error => console.error('Error:', error));
}


document.addEventListener("DOMContentLoaded", function() {
  var modalElement = document.getElementById('notifications-modal');
  
  if (modalElement) {
      var myModal = new bootstrap.Modal(modalElement);
      myModal.show();
  }
});

function updateNotification(notificationId, btn) {
  var csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value; 
  
  fetch(`/update-notification/${notificationId}/`, {
          method: 'POST',
          headers: {
              'X-CSRFToken': csrfToken,
              'Content-Type': 'application/json',
          },
      })
      .then(response => response.json())
      .then(data => {
          if (data.status === 'success') {
              btn.textContent = "Notifikace se příště již nebude zobrazovat";
              btn.disabled = true;
              btn.classList.remove('btn-primary');
              btn.classList.add('btn-secondary');
          } else {
              console.error(data.message);
          }
      })
      .catch(error => console.error('Error:', error));
}

// ---------------------
// 1. Dark Mode Toggle
// ---------------------

const toggleThemeButton = document.getElementById('toggle-checkbox-dark-mode');
const body = document.body;

// Check localStorage for theme preference
if (localStorage.getItem('theme') === 'dark') {
    body.classList.add('dark-mode');
    toggleThemeButton.checked = true;  // Ensure the checkbox reflects the current theme
}

// Listen for theme toggle changes
toggleThemeButton.addEventListener('change', () => {
    if (toggleThemeButton.checked) {
        body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
    } else {
        body.classList.remove('dark-mode');
        localStorage.setItem('theme', 'light');
    }
});


// ----------------------------
// 2. Balance Visibility Toggle
// ----------------------------

let hideBalance = getCookie('hideBalance') === 'true';

const hideBalanceCheckbox = document.getElementById('toggle-checkbox-hide-balance');

function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = `expires=${date.toUTCString()}`;
    document.cookie = `${name}=${value};${expires};path=/`;
}

function getCookie(name) {
    const nameEQ = `${name}=`;
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.indexOf(nameEQ) === 0) {
            return cookie.substring(nameEQ.length, cookie.length);
        }
    }
    return null;
}

function toggleBalance() {
    hideBalance = !hideBalance;
    setCookie('hideBalance', hideBalance, 30);
    renderBalance();
    hideBalanceCheckbox.checked = hideBalance;
}

function renderBalance() {
    const balanceContainer = document.getElementById('balance-container');
    if (!hideBalance) {
        const balance = parseFloat(balanceContainer.getAttribute('data-balance'));
        const formattedBalance = new Intl.NumberFormat('cs-CZ').format(balance); // Format: 69420 -> 69 420
        balanceContainer.innerHTML = `<div onclick="toggleBalance()" id="balance">${formattedBalance} Kč</div>`;
    } else {
        balanceContainer.innerHTML = `<div onclick="toggleBalance()" id="balance">Zůstatek skryt</div>`;
    }
}

function updateBalance(updatedBalance) {
    const balanceContainer = document.getElementById('balance-container');
    const formattedBalance = new Intl.NumberFormat('cs-CZ').format(updatedBalance);

    balanceContainer.setAttribute("data-balance", updatedBalance);
    if (!hideBalance) {
        balanceContainer.innerHTML = `<div onclick="toggleBalance()" id="balance">${formattedBalance} Kč</div>`;
    }
}

hideBalanceCheckbox.addEventListener('change', function () {
    toggleBalance();
});

// Initial 
renderBalance();
hideBalanceCheckbox.checked = hideBalance;

// ----------------------------------------
// 3. Copy User ID to Clipboard. NOT related to actual notifications system
// ----------------------------------------

document.getElementById('user-id').addEventListener('click', function() {
    const userId = this.getAttribute('data-user-id');
    navigator.clipboard.writeText(userId).then(() => {
        showNotification('ID copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
});

window.onload = function() {
  const notification = document.getElementById('notification-copied-id');
  notification.style.transition = 'none';

  setTimeout(() => {
      notification.style.transition = 'opacity .5s, visibility .5s ease';
  }, 500);
};

function showNotification(message) {
  const notification = document.getElementById('notification-copied-id');
  notification.textContent = message;
  notification.classList.add('show');
  
  setTimeout(() => {
      notification.classList.remove('show');
  }, 2000);
}