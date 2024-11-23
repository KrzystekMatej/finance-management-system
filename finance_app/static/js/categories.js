function deleteCategory()
{
    const message = "Opravdu chcete smazat tuto kategorii? " +
                "Pokud máte transakce, které jsou přiřazeny k této kategorii, " +
                "pak se po smazání všechny přiřadí k výchozí kategorii \"Ostatní\".";

    const userConfirmed = confirm(message);

    if (!userConfirmed) {
        return;
    }

    const categoryPreferenceId = this.dataset.categoryPreferenceId;

    fetch(`/delete-category/${categoryPreferenceId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const formElement = this.closest(".edit-category-form");
            if (formElement) {
                formElement.remove();
            }
        }
        alert(data.message);
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Došlo k chybě při mazání kategorie.");
    });
}

function editCategory()
{
    const form = this.closest('.edit-category-form');

    const formData = new FormData(form);
    let isValid = true;

    const nameField = form.elements['name'];
    if (!nameField.value.trim()) {
        nameField.classList.add("is-invalid");
        isValid = false;
    } else {
        nameField.classList.remove("is-invalid");
    }

    const categoryPreferenceId = this.dataset.categoryPreferenceId;
    console.log("ahoj")
    //ToDo the form should not be sent if it was not changed at all
    if(isValid) {
        fetch(`/edit-category/${categoryPreferenceId}/`, {
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

document.querySelectorAll(".delete-category-btn").forEach(button => {
    button.addEventListener("click", deleteCategory);
});





document.querySelectorAll(".edit-category-btn").forEach(button => {
    button.addEventListener("click", editCategory);
});

