const transactionModal = new bootstrap.Modal(document.getElementById('transaction-modal'));
const categoryModal = new bootstrap.Modal(document.getElementById('category-modal'));

window.transactionModalIsHiding = false;

function openModal(hideModal, showModal) {
    window.transactionModalIsHiding = true;
    hideModal.hide();
    showModal.show();
}

document.getElementById('open-transaction-category-modal').addEventListener('click', function() {
    openModal(transactionModal, categoryModal);
});


document.getElementById('category-modal').addEventListener('hidden.bs.modal', function() {
    if (transactionModalIsHiding) {
        window.transactionModalIsHiding = false;
        transactionModal.show();
    }
});

const TimeInterval = {
    DAY: 'DAY',
    WEEK: 'WEEK',
    MONTH: 'MONTH',
    YEAR: 'YEAR',
};

function getNextDate(baseDate, interval) {
    const base = new Date(baseDate);
    switch (interval) {
        case TimeInterval.DAY:
            return new Date(base.setDate(base.getDate() + 1));

        case TimeInterval.WEEK:
            return new Date(base.setDate(base.getDate() + 7));

        case TimeInterval.MONTH: {
            const nextMonth = (base.getMonth() + 1) % 12;
            const year = base.getFullYear() + (nextMonth === 0 ? 1 : 0);
            const lastDayOfNextMonth = new Date(year, nextMonth + 1, 0).getDate();

            const day = Math.min(base.getDate(), lastDayOfNextMonth);
            base.setFullYear(year);
            base.setMonth(nextMonth);
            base.setDate(day);
            return base;
        }

        case TimeInterval.YEAR:
            try {
                base.setFullYear(base.getFullYear() + 1);
                return base;
            } catch (error) {
                base.setFullYear(base.getFullYear() + 1);
                base.setDate(28); // Handle leap year edge cases
                return base;
            }

        default:
            throw new Error('Invalid TimeInterval');
    }
}

function computeGeneratedTransactionCount(lastPerformedAt, interval) {
    const currentTime = new Date();
    let nextGenerationDate = new Date(lastPerformedAt);
    let transactionCount = 1;
    while (true) {
        nextGenerationDate = getNextDate(nextGenerationDate, interval);

        if (nextGenerationDate > currentTime) {
            break;
        }

        transactionCount++;
    }

    return transactionCount;
}

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
        const isRecurring = document.getElementById('recurring-transaction-checkbox').checked;

        if (isRecurring)
        {
            const transactionCount = computeGeneratedTransactionCount(performedAtField.value, form.elements["interval"].value)
            const userConfirmed = confirm(
                "Po vytvoření této rekurentní transakce dojde " +
                `k vygenerování ${transactionCount} transakcí. Určitě chcete pokračovat?`
            )

            if (!userConfirmed) return;
        }

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

document.getElementById("recurring-transaction-checkbox").addEventListener("change", function (event) {
    const selectContainer = document.getElementById('interval-select-container');
    if (selectContainer.classList.contains("hidden"))
    {
        selectContainer.classList.remove("hidden")
    }
    else
    {
        selectContainer.classList.add("hidden")
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

        if (isNaN(amount) && char !== ".") {
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