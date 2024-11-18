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

    if(isValid){
        fetch("create-transaction/", {
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