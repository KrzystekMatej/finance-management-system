import { FieldFormatter, FormManager } from './form_management.js';

function deleteRecurringTransaction()
{
    const message = "Opravdu chcete smazat tuto rekurentní transakci?";
    const userConfirmed = confirm(message);

    if (!userConfirmed) return;

    const transactionId = this.dataset.transactionId;

    fetch(`/delete-recurring-transaction/${transactionId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const formElement = this.closest(".edit-recurring-transaction-form");
            if (formElement) {
                formElement.remove();
            }
        }
        alert(data.message);
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Došlo k chybě při mazání rekurentní transakce.");
    });
}

const editRecurringTransactionFormManager = new FormManager();

editRecurringTransactionFormManager.fieldFormatters = [
    new FieldFormatter("amount", value => value.replace(",", "."))
];


document.querySelectorAll(".delete-recurring-transaction-btn").forEach(button => {
    button.addEventListener("click", deleteRecurringTransaction);
});

document.querySelectorAll(".edit-recurring-transaction-btn").forEach(button => {
    button.addEventListener("click", function (event) {
        editRecurringTransactionFormManager.form = button.closest('.edit-recurring-transaction-form');
        editRecurringTransactionFormManager.viewUrl = `/edit-recurring-transaction/${button.dataset.transactionId}/`;
        editRecurringTransactionFormManager.processForm();
    });
});

