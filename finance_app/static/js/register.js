import { FormManager } from './form_management.js';

const registerFormManager = new FormManager();

registerFormManager.form = document.getElementById("register-form");
registerFormManager.viewUrl = "/register/";

document.getElementById("register-btn").addEventListener("click", function (event) {
    registerFormManager.processForm();
});