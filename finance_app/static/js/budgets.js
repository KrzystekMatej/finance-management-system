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

editBudgetFormManager.formLoader = (form) => {
    const formData = new FormData(form);

    const sharedBudgets = [];

    form.querySelectorAll('.shared-users-container > div').forEach(sharedBudgetDiv => {
        const id = sharedBudgetDiv.querySelector('.shared-budget-id').value;
        const isEditor = sharedBudgetDiv.querySelector('.permission-checkbox').checked;
        const permission = isEditor ? "EDIT" : "VIEW";
        const role = sharedBudgetDiv.querySelector('.role-select').value;



        sharedBudgets.push({
            id: id,
            permission: permission,
            role: role,
        });
    });

    const appOn = document.getElementById(`app-notifications-${form.dataset.budgetId}`).checked
    const emailOn = document.getElementById(`email-notifications-${form.dataset.budgetId}`).checked
    let notificationMode = "NONE"

    if (appOn) notificationMode = "APP";
    if (emailOn) notificationMode = "EMAIL";
    if (appOn && emailOn) notificationMode = "APP_EMAIL";

    formData.append('notification_mode', notificationMode);
    formData.append('shared_budgets', JSON.stringify(sharedBudgets));
    return formData;
};


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





function deleteSharedBudget()
{
    const message = "Opravdu chcete odebrat uživatele ze sdíleného rozpočtu?";
    const userConfirmed = confirm(message);

    if (!userConfirmed) {
        return;
    }

    const budgetId = this.dataset.sharedBudgetId;

    fetch(`/delete-shared-budget/${budgetId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const formElement = this.closest(".shared-budget-container");
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


document.querySelectorAll(".delete-shared-budget-btn").forEach(button => {
    button.addEventListener("click", deleteSharedBudget);
});

