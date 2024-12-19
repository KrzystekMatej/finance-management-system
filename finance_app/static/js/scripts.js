import { CzechNumberInput } from './czech_number_field.js';

document.addEventListener("DOMContentLoaded", () => {
    const czechNumberInputs = document.querySelectorAll(".czech-number");

    czechNumberInputs.forEach((inputElement) => {
        new CzechNumberInput(inputElement);
    });
});
