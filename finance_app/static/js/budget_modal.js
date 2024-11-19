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
        fetch("/create-budget/", {
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