const createTransactionUrl = document.getElementById("transaction-modal").getAttribute("data-create-transaction-url");
const createCategoryUrl = document.getElementById("custom-category-modal").getAttribute("data-create-category-url");

document.getElementById("submit-transaction-btn").addEventListener("click", function () {
    const form = document.getElementById("create-transaction-form");
    const formData = new FormData(form);

    fetch(createTransactionUrl, {
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
});


document.getElementById("submit-category-btn").addEventListener("click", function (event) {
    event.preventDefault();

    const form = document.getElementById("create-category-form");
    const formData = new FormData(form);

    fetch(createCategoryUrl, {
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
            closeCustomCategoryModal()
            location.reload(); // ToDo: close only the category modal and show updated transaction modal
        } else {
            alert("Došlo k chybě při vytváření kategorie.");
        }
    })
    .catch(error => console.error("Error:", error));
});

function closeCustomCategoryModal() {
    const customCategoryModal = bootstrap.Modal.getInstance(document.getElementById('custom-category-modal'));
    customCategoryModal.hide();
    console.log("close custom")
    const previousModal = bootstrap.Modal.getInstance(document.getElementById('transaction-modal'));
    previousModal.show();
}