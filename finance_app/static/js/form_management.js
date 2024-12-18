export class FormManager {
    form;
    viewUrl;
    fieldValidators;

    constructor() {
        this.fieldValidators = [];
    }

    loadFormData() {
        this.formData = new FormData(this.form);
    }

    getFormErrors() {
        const formErrors = new Map();

        for (const validator in this.fieldValidators)
        {
            const message = validator.validate(this.formData)
            if (message !== null)
            {
                formErrors[validator.fieldName] = message;
            }
        }

        return formErrors;
    }

    sendRequest() {
        return fetch(this.viewUrl, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": this.formData.get("csrfmiddlewaretoken"),
            },
            body: this.formData,
        });
    }

    writeErrors(formErrors) {
        for (const element of this.form.elements) {
            const fieldName = element.name;
            const feedbackId = `${fieldName}-feedback`;
            let feedbackElement = document.getElementById(feedbackId);

            if (formErrors[fieldName]) {
                element.classList.add("is-invalid");

                if (feedbackElement) {
                    feedbackElement.textContent = formErrors[fieldName];
                } else {
                    feedbackElement = document.createElement("div");
                    feedbackElement.id = feedbackId;
                    feedbackElement.className = "invalid-feedback";
                    feedbackElement.textContent = formErrors[fieldName];

                    element.insertAdjacentElement("afterend", feedbackElement);
                }
            } else {
                element.classList.remove("is-invalid");

                if (feedbackElement) {
                    feedbackElement.remove();
                }
            }
        }
    }

    validate()
    {
        const formErrors = this.getFormErrors();
        this.writeErrors(formErrors);
        return formErrors.size > 0;
    }

    processResponse(response)
    {
        response.then(response => response.json())
        .then(data => {
            this.writeErrors(data.errors);
        })
        .catch(error => console.error("Error:", error));
    }

    process() {
        this.loadFormData();
        if (this.validate())
        {
            const response = this.sendRequest();
            this.processResponse(response)
        }
    }
}

export class FieldValidator {
    constructor(fieldName, validators) {
        this.fieldName = fieldName;
        this.validators = validators;
    }

    validate(formData) {
        const fieldValue = formData.get(this.fieldName);
        for (const validator of this.validators)
        {
            if (!validator.isValid(fieldValue))
            {
                return validator.errorMessage;
            }
        }
        return null;
    }
}


export class Validator {
    constructor(validationFunction, errorMessage) {
        this.validationFunction = validationFunction;
        this.errorMessage = errorMessage;
    }

    isValid(value) {
        return this.validationFunction(value);
    }
}