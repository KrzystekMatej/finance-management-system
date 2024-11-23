document.querySelectorAll(".delete-transaction").forEach(button => {
    button.addEventListener(
        "click",
        function () {
            const userConfirmed = confirm("Opravdu chcete smazat tuto transakci?");

            if (!userConfirmed) {
                return;
            }

            const transactionId = this.dataset.transactionId;

            fetch(`/delete-transaction/${transactionId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const transactionElement = this.closest(".transaction");
                        if (transactionElement) {
                            transactionElement.remove();
                        }
                    }
                    alert(data.message);
                })
                .catch(error => {
                    console.error("Error:", error);
                    alert("Došlo k chybě při mazání transakce.");
                });
        },
    );
});