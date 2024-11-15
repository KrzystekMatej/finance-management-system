const createTransactionUrl = document.getElementById("transaction-modal").getAttribute("data-create-transaction-url");
const createCategoryUrl = document.getElementById("custom-category-modal").getAttribute("data-create-category-url");
const createBudgetUrl = document.getElementById("budget-modal").getAttribute("data-create-budget-url");

document.getElementById("submit-transaction-btn").addEventListener("click", function (event) {
    event.preventDefault();

    const form = document.getElementById("create-transaction-form");
    const formData = new FormData(form);
    let isValid = true;
    // ToDo - messages
    const amountField = document.getElementById("transaction-amount");
    if (!amountField.value || isNaN(amountField.value)) {
        amountField.classList.add("is-invalid");
        isValid = false;
    } else {
        amountField.classList.remove("is-invalid");
    }

    const dateField = document.getElementById("transaction-date");
    if (!dateField.value) {
        dateField.classList.add("is-invalid");
        isValid = false;
    } else {
        const inputDate = new Date(dateField.value);
        const currentDate = new Date();

        if (inputDate > currentDate) {
            dateField.classList.add("is-invalid");
            isValid = false;
            // ToDo - message - "Datum a čas transakce nesmí být v budoucnosti."
        } else {
            dateField.classList.remove("is-invalid");
        }
    }

    const categoryField = document.getElementById("transaction-category-select");
    if (!categoryField.value) {
        categoryField.classList.add("is-invalid");
        isValid = false;
    } else {
        categoryField.classList.remove("is-invalid");
    }

    const nameField = document.getElementById("transaction-name");
    if (!nameField.value.trim()) {
        nameField.classList.add("is-invalid");
        isValid = false;
    } else {
        nameField.classList.remove("is-invalid");
    }

    if(isValid){
        fetch(createTransactionUrl, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $('#transaction-modal').modal('hide');
                location.reload();
            } else {
                alert("Došlo k chybě při vytváření transakce.");
            }
        })
        .catch(error => console.error("Error:", error));
    }
});


document.getElementById("submit-category-btn").addEventListener("click", function (event) {
    event.preventDefault();

    const form = document.getElementById("create-category-form");
    const formData = new FormData(form);
    let isValid = true;

    const nameField = document.getElementById("custom-category-name");
    if (!nameField.value.trim()) {
        nameField.classList.add("is-invalid");
        isValid = false;
    } else {
        nameField.classList.remove("is-invalid");
    }

    if(isValid){
        fetch(createCategoryUrl, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Kategorie byla vytvořena!");
                const newCategoryPreference = data.category_preference;
                const categorySelect = document.getElementById("transaction-category-select");
                const newOption = document.createElement("option");
                newOption.value = newCategoryPreference.category.id;
                newOption.textContent = newCategoryPreference.category.name;
                categorySelect.appendChild(newOption);
                console.log(newCategoryPreference)
                document.getElementById("close-custom-category-modal-top").click();

                document.getElementById('transaction-modal').addEventListener('shown.bs.modal', function () {
                    categorySelect.value = newCategoryPreference.category.id;
                }, { once: true });
            } else {
                alert("Došlo k chybě při vytváření kategorie.");
            }
        })
        .catch(error => console.error("Error:", error));
    }
});

document.getElementById("submit-budget-btn").addEventListener("click", function (event) {
    event.preventDefault();

    const form = document.getElementById("create-budget-form");
    const formData = new FormData(form);
    let isValid = true;

    const nameField = document.getElementById("budget-name");
    if (!nameField.value.trim()) {
        nameField.classList.add("is-invalid");
        isValid = false;
    } else {
        nameField.classList.remove("is-invalid");
    }

    const categoriesField = document.getElementById("budget-categories");
    if (!categoriesField.selectedOptions.length) {
        categoriesField.classList.add("is-invalid");
        isValid = false;
    } else {
        categoriesField.classList.remove("is-invalid");
    }

    const limitField = document.getElementById("budget-limit");
    const periodStartField = document.getElementById("budget-from");
    const periodEndField = document.getElementById("budget-to");

    const limitProvided = limitField.value;
    const periodStartProvided = periodStartField.value;
    const periodEndProvided = periodEndField.value;

    if ((limitProvided || periodStartProvided || periodEndProvided) &&
        (!limitProvided || !periodStartProvided || !periodEndProvided)) {
        limitField.classList.add("is-invalid");
        periodStartField.classList.add("is-invalid");
        periodEndField.classList.add("is-invalid");
        isValid = false;
    } else {
        limitField.classList.remove("is-invalid");
        periodStartField.classList.remove("is-invalid");
        periodEndField.classList.remove("is-invalid");
    }

    if(isValid){
        fetch(createBudgetUrl, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Rozpočet byl vytvořen!");
                $('#budget-modal').modal('hide');
                location.reload();
            } else {
                alert("Došlo k chybě při vytváření rozpočtu.");
            }
        })
        .catch(error => console.error("Error:", error));
    }
});

  // Delete transaction
  $(document).ready(function() {
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');

  $('.delete-transaction').on('click', function() {
    const transactionId = $(this).data('transaction-id');
    if (confirm('Opravdu chcete smazat tuhle transakci?')) {
      $.ajax({
        url: `/delete-transaction/${transactionId}/`,
        type: 'POST',
        headers: { 'X-CSRFToken': csrftoken },
        success: function(response) {
          if (response.success) {
            alert('Transakce smazána. Obnovuji stránku [TODO livereload?]');
            // TODO: Livereload
            location.reload();
          }
        },
        error: function(xhr) {
          console.error('Nastala chyba při mazání transakce.');
        }
      });
    }
  });
});