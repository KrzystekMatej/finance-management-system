
export class CzechNumberInput {
    constructor(inputElement) {
        this.inputElement = inputElement;

        this.inputElement.addEventListener("keypress", this.allowValidCharacters.bind(this));
        this.inputElement.addEventListener("paste", this.validatePastedInput.bind(this));
    }

    allowValidCharacters(event) {
        const allowedKeys = ["Backspace", "ArrowLeft", "ArrowRight", "Delete", "Tab"];
        const char = event.key;

        if (allowedKeys.includes(char)) return;

        if ((char === "+" || char === "-") && this.inputElement.selectionStart === 0) {
            return;
        }

        const regex = /^[0-9]$/;
        if (!regex.test(char) && char !== ",") {
            event.preventDefault();
        }

        if (char === "," && this.inputElement.value.includes(",")) {
            event.preventDefault();
        }
    }

    validatePastedInput(event) {
        const clipboardData = event.clipboardData || window.clipboardData;
        const pastedText = clipboardData.getData("text");

        const regex = /^[+-]?\d*(,\d+)?$/;
        if (!regex.test(pastedText)) {
            event.preventDefault();
        }
    }
}