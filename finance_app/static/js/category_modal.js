function updateCategoriesView(newCategoryPreference)
{
    const tableBody = document.getElementById("categories-table-body");

    const newForm = document.createElement("form");
    newForm.classList.add("edit-category-form", "d-flex", "align-items-center", "mb-2");
    newForm.method = "post";
    newForm.action = "";

    const csrfInput = document.createElement("input");
    csrfInput.type = "hidden";
    csrfInput.name = "csrfmiddlewaretoken";
    csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
    newForm.appendChild(csrfInput);

    const newRow = document.createElement("div");
    newRow.classList.add("category-row", "d-flex", "align-items-center", "w-100");
    newRow.dataset.categoryPreferenceId = newCategoryPreference.id;

    newRow.innerHTML = `
        <div class="category-name flex-grow-1">
            <input type="text" name="name" class="form-control category-name" value="${newCategoryPreference.category.name}">
        </div>
        <div class="category-color d-flex align-items-center flex-grow-1 px-2">
            <input type="color" name="color" class="form-control form-control-color category-color me-2" value="${newCategoryPreference.color}">
        </div>
        <div class="edit-actions text-center px-2">
            <button type="button" class="btn btn-link p-0 edit-category-btn" data-category-preference-id="${newCategoryPreference.id}">
                <i class="fas fa-save text-primary"></i>
            </button>
        </div>
        <div class="delete-actions text-center px-2">
            <button type="button" class="btn btn-link p-0 delete-category-btn" data-category-preference-id="${newCategoryPreference.id}">
                <i class="fas fa-trash-alt text-danger"></i>
            </button>
        </div>
    `;

    newForm.appendChild(newRow);
    tableBody.appendChild(newForm);

    const editButton = newRow.querySelector(".edit-category-btn");
    const deleteButton = newRow.querySelector(".delete-category-btn");

    editButton.addEventListener("click", editCategory);
    deleteButton.addEventListener("click", deleteCategory);
}


document.getElementById("submit-category-btn").addEventListener("click", function (event) {
    event.preventDefault();

    const form = document.getElementById("create-category-form");
    const formData = new FormData(form);
    let isValid = true;

    const nameField = form.elements['name'];
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
                    updateCategoriesView(newCategoryPreference)
                }

                document.getElementById("close-category-modal-top").click();
            }
            alert(data.message);
        })
        .catch(error => console.error("Error:", error));
    }
});