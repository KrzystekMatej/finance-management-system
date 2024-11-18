document.getElementById("submit-category-btn").addEventListener("click", function (event) {
    event.preventDefault();

    const form = document.getElementById("create-category-form");
    const formData = new FormData(form);
    let isValid = true;

    const nameField = document.getElementById("custom-category-name");
    if (!nameField.value.trim()) {
        nameField.classList.add("is-invalid");
        isValid = false;
    } else {
        nameField.classList.remove("is-invalid");
    }

    if(isValid){
        fetch("create-category/", {
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
                alert("Kategorie byla vytvořena!");
                const newCategoryPreference = data.category_preference;
                const categorySelect = document.getElementById("transaction-category-select");
                const newOption = document.createElement("option");
                newOption.value = newCategoryPreference.category.id;
                newOption.textContent = newCategoryPreference.category.name;
                categorySelect.appendChild(newOption);
                console.log(newCategoryPreference)
                document.getElementById("close-custom-category-modal-top").click();

                document.getElementById('transaction-modal').addEventListener('shown.bs.modal', function () {
                    categorySelect.value = newCategoryPreference.category.id;
                }, { once: true });
            } else {
                alert("Došlo k chybě při vytváření kategorie.");
            }
        })
        .catch(error => console.error("Error:", error));
    }
});