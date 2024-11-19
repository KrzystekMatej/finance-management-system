

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

document.getElementById("edit-transaction-btn").addEventListener("click", function (event) {
    const form = document.getElementById("edit-transaction-form");
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

    const dateField = document.getElementById("transaction-performed-at");
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

    console.log(isValid)
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
            if (data.success) {
                alert("Změny úspěšně uloženy.");
            } else {
                alert("Došlo k chybě při ukládání transakce.");
            }
        })
        .catch(error => console.error("Error:", error));
    }
});