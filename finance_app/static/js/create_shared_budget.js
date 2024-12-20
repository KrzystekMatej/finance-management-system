import { FormManager } from './form_management.js';


const createSharedBudgetFormManager = new FormManager();

createSharedBudgetFormManager.viewUrl = "/create-shared-budget/";
createSharedBudgetFormManager.form = document.getElementById("add-user-form");

createSharedBudgetFormManager.formLoader = (form) => {
    const formData = new FormData(form);
    const appOn = document.getElementById(`app-notifications`).checked
    const emailOn = document.getElementById(`email-notifications`).checked
    let notificationMode = "NONE"

    if (appOn) notificationMode = "APP";
    if (emailOn) notificationMode = "EMAIL";
    if (appOn && emailOn) notificationMode = "APP_EMAIL";
    formData.append('_notification_mode', notificationMode);

    return formData;
};

createSharedBudgetFormManager.postSuccess = (data) => {
    location.reload();
};

document.getElementById("create-shared-budget-btn").addEventListener("click", function (event) {
    createSharedBudgetFormManager.processForm();
});

