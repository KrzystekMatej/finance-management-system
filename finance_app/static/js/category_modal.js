
document.getElementById("submit-category-btn").addEventListener("click", function (event) {
    event.preventDefault();

    const form = document.getElementById("create-category-form");
    const formData = new FormData(form);
    let isValid = true;

    const nameField = document.getElementById("category-name");
    if (!nameField.value.trim()) {
        nameField.classList.add("is-invalid");
        isValid = false;
    } else {
        nameField.classList.remove("is-invalid");
    }

    if(isValid) {
        fetch("/create-category/", {
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

                if (window.transactionModalIsHiding) {
                    const categorySelect = document.getElementById("transaction-category-select");
                    const newOption = document.createElement("option");
                    newOption.value = newCategoryPreference.category.id;
                    newOption.textContent = newCategoryPreference.category.name;
                    categorySelect.appendChild(newOption);
                    document.getElementById("transaction-modal").addEventListener('shown.bs.modal', function () {
                        categorySelect.value = newCategoryPreference.category.id;
                    }, { once: true });
                }

                if (window.location.pathname === "/categories/") {
                    const tableBody = document.getElementById("categories-table-body");
                    const newRow = document.createElement("tr");
                    newRow.dataset.categoryPreferenceId = newCategoryPreference.id;

                    newRow.innerHTML = `
                        <td>
                            <input type="text" class="form-control category-name" value="${newCategoryPreference.category.name}">
                        </td>
                        <td class="d-flex align-items-center">
                            <input type="color" class="form-control form-control-color category-color me-2" value="${newCategoryPreference.color}">
                        </td>
                        <td class="text-center">
                            <button type="button" class="btn btn-link p-0 edit-category" data-category-preference-id="${newCategoryPreference.id}">
                                <i class="fas fa-save text-primary"></i>
                            </button>
                        </td>
                        <td class="text-center">
                            <button type="button" class="btn btn-link p-0 delete-category" data-category-preference-id="${newCategoryPreference.id}">
                                <i class="fas fa-trash-alt text-danger"></i>
                            </button>
                        </td>
                    `;

                    tableBody.appendChild(newRow);
                }

                document.getElementById("close-category-modal-top").click();
            } else {
                alert("Došlo k chybě při vytváření kategorie.");
            }
        })
        .catch(error => console.error("Error:", error));
    }
});