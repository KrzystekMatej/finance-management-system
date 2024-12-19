import {FieldFormatter, FormManager} from './form_management.js';

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

const editBudgetFormManager = new FormManager();

editBudgetFormManager.fieldFormatters = [
    new FieldFormatter("limit", value => value.replace(",", "."))
];


document.querySelectorAll(".delete-budget-btn").forEach(button => {
    button.addEventListener("click", deleteBudget);
});

document.querySelectorAll(".edit-budget-btn").forEach(button => {
    button.addEventListener("click", function (event) {
        editBudgetFormManager.form = button.closest('.edit-budget-form');
        editBudgetFormManager.viewUrl = `/edit-budget/${button.dataset.budgetId}/`;
        editBudgetFormManager.processForm();
    });
});

