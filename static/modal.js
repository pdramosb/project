document.addEventListener("DOMContentLoaded", () => {
    // Abrir modal
    document.querySelectorAll(".column").forEach(column => {
        column.addEventListener("click", () => {
            const modalId = column.getAttribute("data-modal");
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = "block";
            }
        });
    });

    // Cerrar modal
    document.querySelectorAll(".modal .close").forEach(closeBtn => {
        closeBtn.addEventListener("click", () => {
            const modal = closeBtn.closest(".modal");
            if (modal) {
                modal.style.display = "none";
            }
        });
    });

    // Cerrar modal al hacer clic fuera del contenido
    document.querySelectorAll(".modal").forEach(modal => {
        modal.addEventListener("click", (event) => {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    });
});
