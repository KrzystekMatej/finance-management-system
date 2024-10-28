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

// ----------------------
// 6. Create transaction functions
// ----------------------

document.getElementById('recurrent-transaction').addEventListener('change', function () {
  const recurrenceOptions = document.getElementById('recurrence-options');
  recurrenceOptions.style.display = this.checked ? 'block' : 'none';
});

document.getElementById('recurrence-frequency').addEventListener('change', function () {
  const weeklyOptions = document.getElementById('weekly-options');
  const monthlyOptions = document.getElementById('monthly-options');
  
  // Reset options display
  weeklyOptions.style.display = 'none';
  monthlyOptions.style.display = 'none';

  if (this.value === 'weekly') {
    weeklyOptions.style.display = 'block';
  } else if (this.value === 'monthly') {
    monthlyOptions.style.display = 'block';
  }
});

  function saveCustomCategory() {
    const categoryName = document.getElementById('custom-category-name').value;
    const categoryColor = document.getElementById('custom-category-color-input').value;

    // TODO: Create new category database entry for this
    console.log("Category Name:", categoryName);
    console.log("Category Color:", categoryColor);

    closeCustomCategoryModal();
}

function closeCustomCategoryModal() {
    const customCategoryModal = bootstrap.Modal.getInstance(document.getElementById('custom-category-modal'));
    customCategoryModal.hide();
    const previousModal = bootstrap.Modal.getInstance(document.getElementById('transaction-modal'));
    previousModal.show();
}

function saveRecurrenceSettings() {
  const recurrenceFrequency = document.getElementById('recurrence-frequency-modal').value;
  const weeklyDay = document.getElementById('weekly-day').value;
  const monthlyDay = document.getElementById('monthly-day').value;

  // TODO: Save recurrence settings logic here
  console.log("Recurrence Frequency:", recurrenceFrequency);
  console.log("Weekly Day:", weeklyDay);
  console.log("Monthly Day:", monthlyDay);

  closeRecurrenceModal();
}

function openRecurrenceModal() {
  const recurrenceModal = new bootstrap.Modal(document.getElementById('recurrence-modal'));
  recurrenceModal.show();
  
  // Call the update function to ensure correct options are displayed
  updateRecurrenceOptions();
}


function closeRecurrenceModal() {
  const recurrenceModal = bootstrap.Modal.getInstance(document.getElementById('recurrence-modal'));
  recurrenceModal.hide();
  const previousModal = bootstrap.Modal.getInstance(document.getElementById('transaction-modal'));
  previousModal.show();
}

function toggleRecurrenceModal() {
  const isChecked = document.getElementById('recurrent-transaction').checked;
  const setRecurrenceButton = document.getElementById('set-recurrence-btn');
  
  setRecurrenceButton.disabled = !isChecked;
}

function updateRecurrenceOptions() {
  const frequency = document.getElementById('recurrence-frequency-modal').value;
  
  document.getElementById('weekly-options-modal').style.display = 'none';
  document.getElementById('monthly-options-modal').style.display = 'none';
  document.getElementById('yearly-options-modal').style.display = 'none';
  
  // Show the relevant option based on selected frequency
  if (frequency === 'weekly') {
      document.getElementById('weekly-options-modal').style.display = 'block';
  } else if (frequency === 'monthly') {
      document.getElementById('monthly-options-modal').style.display = 'block';
  } else if (frequency === 'yearly') {
      document.getElementById('yearly-options-modal').style.display = 'block';
  }
}

