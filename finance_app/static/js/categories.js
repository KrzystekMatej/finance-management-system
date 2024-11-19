

document.querySelectorAll(".delete-category-btn").forEach(button => {
    button.addEventListener(
        "click",
        function () {
            const userConfirmed = confirm("Opravdu chcete smazat tuto kategorii?");

            if (!userConfirmed) {
                return;
            }

            const categoryPreferenceId = this.dataset.categoryPreferenceId;

            fetch(`/delete-category/${categoryPreferenceId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const categoryRowElement = this.closest("tr");
                        if (categoryRowElement) {
                            categoryRowElement.remove();
                        }
                    } else {
                        alert("Nepodařilo se smazat kategorii.");
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    alert("Došlo k chybě při mazání kategorie.");
                });
        },
    );
});


document.querySelectorAll(".edit-category-btn").forEach(button => {
    button.addEventListener(
        "click",
        function () {

            const form = this.closest('.edit-category-form');

            if (!form) {
                console.error("Form not found!");
                return;
            }
            else {
                console.error("Form found!");
                return;
            }


            const formData = new FormData(form);
            let isValid = true;

            const nameField = document.getElementById("category-name");
            if (!nameField.value.trim()) {
                nameField.classList.add("is-invalid");
                isValid = false;
            } else {
                nameField.classList.remove("is-invalid");
            }

            const categoryPreferenceId = this.dataset.categoryPreferenceId;

            if(isValid) {
                fetch(`/edit-category/${categoryPreferenceId}/`, {
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
                        alert("Změny byly úspěšně uloženy!");
                    } else {
                        alert("Došlo k chybě při ukládání změn.");
                    }
                })
                .catch(error => console.error("Error:", error));
            }
        },
    );
});