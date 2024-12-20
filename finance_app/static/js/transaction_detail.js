import { FormManager, FieldFormatter } from './form_management.js';

const editTransactionFormManager = new FormManager();

editTransactionFormManager.form = document.getElementById("edit-transaction-form");
editTransactionFormManager.viewUrl = `/transaction/${editTransactionFormManager.form.dataset.transactionId}/`;

editTransactionFormManager.fieldFormatters = [
    new FieldFormatter("amount", value => value.replace(",", "."))
];

editTransactionFormManager.postSuccess = (data) => {
    updateBalance(data.balance);
};

document.getElementById("edit-transaction-btn").addEventListener("click", function (event) {
    editTransactionFormManager.processForm();
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
                updateBalance(data.balance);
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