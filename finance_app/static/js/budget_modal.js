import {FieldFormatter, FormManager} from './form_management.js';

const createBudgetFormManager = new FormManager();

createBudgetFormManager.form = document.getElementById("create-budget-form");
createBudgetFormManager.viewUrl = "/create-budget/";

createBudgetFormManager.postSuccess = () => {
    $('#budget-modal').modal('hide');
    location.reload();
};

createBudgetFormManager.fieldFormatters = [
    new FieldFormatter("limit", value => value.replace(",", "."))
];



document.getElementById("submit-budget-btn").addEventListener("click", function (event) {
    createBudgetFormManager.processForm();
});