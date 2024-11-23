function deleteBudget()
{
    const message = "Opravdu chcete smazat tento rozpočet?";
    const userConfirmed = confirm(message);

    if (!userConfirmed) {
        return;
    }

    const budgetId = this.dataset.budgetId;

    fetch(`/delete-budget/${budgetId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const formElement = this.closest(".edit-budget-form");
            if (formElement) {
                formElement.remove();
            }
        }
        alert(data.message);
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Došlo k chybě při mazání rozpočtu.");
    });
}

function editBudget() {
    const form = this.closest(".edit-budget-form");
    const formData = new FormData(form);
    let isValid = true;

    const nameField = form.elements["name"];
    if (!nameField.value.trim()) {
        nameField.classList.add("is-invalid");
        isValid = false;
    } else {
        nameField.classList.remove("is-invalid");
    }

    const categoriesField = form.querySelectorAll("input[name='categories']:checked");
    if (!categoriesField.length) {
        const categoriesContainer = form.querySelector(".budget-categories");
        categoriesContainer.classList.add("is-invalid");
        isValid = false;
    } else {
        const categoriesContainer = form.querySelector(".budget-categories");
        categoriesContainer.classList.remove("is-invalid");
    }

    const limitField = form.elements["limit"];
    const periodStartField = form.elements["period_start"];
    const periodEndField = form.elements["period_end"];

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

    const formattedLimit = limitField.value.replace(",", ".");
    formData.set("limit", formattedLimit);

    const budgetId = this.dataset.budgetId;
    for (let pair of formData.entries()) {
        console.log(pair[0] + ": " + pair[1]);
    }
    // ToDo: Prevent sending the form if it has not been changed
    if (isValid) {
        fetch(`/edit-budget/${budgetId}/`, {
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
}


document.querySelectorAll(".delete-budget-btn").forEach(button => {
    button.addEventListener("click", deleteBudget);
});

document.querySelectorAll(".edit-budget-btn").forEach(button => {
    button.addEventListener("click", editBudget);
});

