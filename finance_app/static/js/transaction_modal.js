const transactionModal = new bootstrap.Modal(document.getElementById('transaction-modal'));
const categoryModal = new bootstrap.Modal(document.getElementById('category-modal'));
const recurrenceModal = new bootstrap.Modal(document.getElementById('recurrence-modal'));

window.transactionModalIsHiding = false;

function openModal(hideModal, showModal) {
    window.transactionModalIsHiding = true;
    hideModal.hide();
    showModal.show();
}

document.getElementById('open-transaction-category-modal').addEventListener('click', function() {
    openModal(transactionModal, categoryModal);
});

document.getElementById('open-recurrence-modal').addEventListener('click', function() {
    openModal(transactionModal, recurrenceModal);
});

['category-modal', 'recurrence-modal'].forEach(modalId => {
    document.getElementById(modalId).addEventListener('hidden.bs.modal', function() {
        if (transactionModalIsHiding) {
            window.transactionModalIsHiding = false;
            transactionModal.show();
        }
    });
});

document.getElementById("submit-transaction-btn").addEventListener("click", function (event) {
    const form = document.getElementById("create-transaction-form");
    const formData = new FormData(form);
    let isValid = true;
    // ToDo - messages
    const amountField = form.elements["transaction-amount"];
    if (!amountField.value || isNaN(amountField.value)) {
        amountField.classList.add("is-invalid");
        isValid = false;
    } else {
        amountField.classList.remove("is-invalid");
    }

    const dateField = form.elements["transaction-performed-at"];
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const selectedDate = new Date(dateField.value);
    if (!dateField.value || selectedDate > today) {
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

    if(isValid){
        fetch("/create-transaction/", {
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
                transactionModal.hide()
                location.reload();//ToDo - live reload
            }
            alert(data.message);
        })
        .catch(error => console.error("Error:", error));
    }
});


// Update value in form depending whether it's incoming or outcoming transaction
document.addEventListener("DOMContentLoaded", function() {

    const amountInput = document.getElementById("transaction-amount");
    const signedAmountInput = document.getElementById("signed-amount");
    const incomingTransaction = document.getElementById("incoming-transaction");
    const outcomingTransaction = document.getElementById("outcoming-transaction");
    let previousSigned = '';
    let previousAmount = '';
    let previousChar = "";

    function updateAmount() {
        let amount = amountInput.value;
        let char = amount.slice(-1);

        if (isNaN(amount) && char != ".") {
            amountInput.value = previousAmount;
            return;
        }

        if ((amount.match(/\./g) || []).length > 1) {
            amountInput.value = previousAmount;
            return;
        }

        amount = parseFloat(amount);

        // signed is the actual value that gets sent in form
        if (outcomingTransaction.checked) {
            signedAmountInput.value = -Math.abs(amount);
        } else {
            signedAmountInput.value = Math.abs(amount);
        }

        previousSigned = signedAmountInput.value;
        previousAmount = amountInput.value;
        previousChar = char;
    }

    amountInput.addEventListener("input", updateAmount);
    incomingTransaction.addEventListener("change", updateAmount);
    outcomingTransaction.addEventListener("change", updateAmount);

});