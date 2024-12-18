import { FormManager, FieldValidator, Validator } from './form_management.js';

const editFormManager = new FormManager()



document.getElementById("edit-transaction-btn").addEventListener("click", function (event) {
    const form = document.getElementById("edit-transaction-form");
    const formData = new FormData(form);
    let isValid = true;
    // ToDo - messages, validation should be on a hidden input (with výdaj/příjem button) - the current will not work in certain cases
    const amountField =  form.elements['transaction-amount'];
    if (!amountField.value || isNaN(amountField.value)) {
        amountField.classList.add("is-invalid");
        isValid = false;
    } else {
        amountField.classList.remove("is-invalid");
    }

    const formattedAmount = amountField.value.replace(",", ".");
    formData.set("transaction-amount", formattedAmount);

    const performedAtField = form.elements["transaction-performed-at"];
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const selectedDate = new Date(performedAtField.value);
    if (!performedAtField.value || selectedDate > today) {
        performedAtField.classList.add("is-invalid");
        isValid = false;
    } else {
        const inputDate = new Date(performedAtField.value);
        const currentDate = new Date();

        if (inputDate > currentDate) {
            performedAtField.classList.add("is-invalid");
            isValid = false;
            // ToDo - message - "Datum a čas transakce nesmí být v budoucnosti."
        } else {
            performedAtField.classList.remove("is-invalid");
        }
    }

    const categoryField = form.elements["transaction-category-select"];
    if (!categoryField.value) {
        categoryField.classList.add("is-invalid");
        isValid = false;
    } else {
        categoryField.classList.remove("is-invalid");
    }

    const nameField = form.elements["transaction-name"];
    if (!nameField.value.trim()) {
        nameField.classList.add("is-invalid");
        isValid = false;
    } else {
        nameField.classList.remove("is-invalid");
    }

    if(isValid) {
        const transactionId = this.dataset.transactionId
        fetch(`/transaction/${transactionId}/`, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => console.error("Error:", error));
    }
});

document.getElementById("delete-transaction-btn").addEventListener("click", function (event) {
    const userConfirmed = confirm("Opravdu chcete smazat tuto transakci?");

    if (!userConfirmed) {
        return;
    }

    const transactionId = this.dataset.transactionId;

    fetch(`/delete-transaction/${transactionId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            "X-Requested-With": "XMLHttpRequest",
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = "/";
            } else {
                alert("Nepodařilo se smazat transakci.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Došlo k chybě při mazání transakce.");
        });
});