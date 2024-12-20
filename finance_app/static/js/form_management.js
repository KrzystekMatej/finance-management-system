export class FormManager {
    form;
    viewUrl;
    fieldFormatters;
    isRequestPending;
    confirmation;
    postSuccess;
    postFailure;
    formLoader;

    constructor() {
        this.fieldFormatters = [];
        this.isRequestPending = false;

        window.addEventListener("beforeunload", (event) => {
            if (this.isRequestPending) {
                event.preventDefault();
            }
        });
    }

    loadFormData() {
        if (this.formLoader) this.formData = this.formLoader(this.form);
        else this.formData = new FormData(this.form);

        for (const formatter of this.fieldFormatters) {
            const value = this.formData.get(formatter.fieldName)
            if (value) {
                const formattedValue = formatter.format(value);
                this.formData.set(formatter.fieldName, formattedValue);
            }
        }
    }

    sendRequest() {
        this.isRequestPending = true;
        return fetch(this.viewUrl, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": this.formData.get("csrfmiddlewaretoken"),
            },
            body: this.formData,
        }).finally(() => {
            this.isRequestPending = false;
        });
    }

    updateFormErrors(formErrors) {
        for (const element of this.form.elements) {
            const fieldName = element.name;
            const feedbackId = `${fieldName}-feedback`;
            let feedbackElement = document.getElementById(feedbackId);

            const errorMessage = formErrors.get(fieldName);

            if (errorMessage !== undefined) {
                element.classList.add("is-invalid");

                if (errorMessage === "" && feedbackElement) {
                    feedbackElement.remove();
                    continue;
                }

                if (feedbackElement) {
                    feedbackElement.textContent = errorMessage;
                    continue;
                }

                feedbackElement = document.createElement("div");
                feedbackElement.id = feedbackId;
                feedbackElement.className = "invalid-feedback";
                feedbackElement.textContent = errorMessage;

                element.insertAdjacentElement("afterend", feedbackElement);
            }
            else {
                element.classList.remove("is-invalid");

                if (feedbackElement) {
                    feedbackElement.remove();
                }
            }
        }
    }

    processResponse(response)
    {
         response.then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updateFormErrors(new Map())
                if (data.message) {
                    alert(data.message);
                }

                if (this.postSuccess) this.postSuccess(data);
            }
            else {
                this.updateFormErrors(new Map(Object.entries(data.errors)));

                if (data.errors["__all__"] && data.errors["__all__"].length > 0) {
                    alert(data.errors["__all__"].join(", "));
                }

                if (this.postFailure) this.postFailure(data);
            }

            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        })
        .catch(error => console.error("Error:", error));
    }

    processForm() {
        this.loadFormData();
        if (this.confirmation && !this.confirmation(this.formData)) return;
        const response = this.sendRequest();
        this.processResponse(response)
    }
}

export class FieldFormatter {
    fieldName;
    formatFunction;

    constructor(fieldName, formatFunction) {
        this.fieldName = fieldName;
        this.formatFunction = formatFunction;
    }

    format(value) {
        return this.formatFunction(value);
    }
}