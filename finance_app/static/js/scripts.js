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

let hideBalance = false; // TODO: Fetch from account's settings

const hideBalanceCheckbox = document.getElementById('toggle-checkbox-hide-balance');

// Function to toggle balance visibility
function toggleBalance() {
    showBalance = !showBalance;
    renderBalance();
}

// Function to render balance depending on visibility settings
function renderBalance() {
  const balanceContainer = document.getElementById('balance-container');
  if (!hideBalance) {
      const balance = parseFloat(balanceContainer.getAttribute('data-balance'));
      const formattedBalance = new Intl.NumberFormat('cs-CZ').format(balance); // 69420 -> 69 420

      balanceContainer.innerHTML = `<div onclick="toggleBalance()" id="balance">` + formattedBalance + ` Kč</div>`;
    }else{
      const balanceElement = document.getElementById('balance');
      if (balanceElement){
        balanceElement.remove();
      }

    }
}

// Event listener for balance hiding toggle
hideBalanceCheckbox.addEventListener('change', function() {
    hideBalance = this.checked;
    renderBalance();
});

// Initial render of the balance section
renderBalance();
hideBalanceCheckbox.checked = hideBalance;

// ----------------------------------------
// 3. Copy User ID to Clipboard
// ----------------------------------------

document.getElementById('user-id').addEventListener('click', function() {
    const userId = this.getAttribute('data-user-id');
    navigator.clipboard.writeText(userId).then(() => {
        showNotification('ID copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
});

// ----------------------
// 4. Notification System
// ----------------------

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

// Brech limit notifications
// If there are no notifications to show, then modal is not inserted into HTMLdoc
// If cookie to not show notifications is set, then it will also not show the modal

const toggleNotificationsButton = document.getElementById('toggle-checkbox-show-notifications');

toggleNotificationsButton.addEventListener('change', () => {
  if (toggleNotificationsButton.checked) {
      document.cookie = "ignore_notifications=true; path=/; max-age=31536000";
  } else {
      document.cookie = "ignore_notifications=false; path=/; max-age=31536000";
  }
});

// Function to get a cookie by its name in a simpler way
function getCookie(name) {
  const cookies = document.cookie.split('; ');
  for (let cookie of cookies) {
    const [key, value] = cookie.split('=');
    if (key === name) {
      return value;
    }
  }
  return null; // Return null if the cookie is not found
}

document.addEventListener("DOMContentLoaded", function() {
  var modalElement = document.getElementById('notifications-modal');
  
  // If true, then user wants to hide the notifications
  var ignore = getCookie('ignore_notifications');
  console.log("Value of cookie:", ignore)

  if (ignore === 'true') {
    toggleNotificationsButton.checked = true;
  } else {
    toggleNotificationsButton.checked = false;
  }
  
  if (modalElement) {
    if (ignore !== 'true'){
      var myModal = new bootstrap.Modal(modalElement);
      myModal.show();
    }
  }
});

// Modal button
document.getElementById('acknowledge-notifications-button').addEventListener('click', function() {
  document.cookie = "ignore_notifications=true; path=/; max-age=31536000";
  toggleNotificationsButton.checked = true;
});
