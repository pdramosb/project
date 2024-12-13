document.addEventListener("DOMContentLoaded", function () {
    const downloadBtn = document.getElementById("download-btn");
    const emailInput = document.getElementById("email-input");
    const emailBtn = document.getElementById("email-btn");

    // Lógica para descargar el archivo
    downloadBtn.addEventListener("click", () => {
        window.location.href = "/download/resultados";
    });

    // Habilitar/deshabilitar el botón de envío según el contenido del input
    emailInput.addEventListener("input", () => {
        emailBtn.disabled = emailInput.value.trim() === "";
    });
});

document.getElementById("email-btn").onclick = function() {
    var email = document.getElementById("email-input").value;
    if (!email) {
        alert("Por favor, ingrese un correo electrónico.");
        return;
    }

    fetch('/send-email', {
        method: 'POST',
        body: new URLSearchParams({
            email: email
        }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Correo enviado correctamente.");
        } else {
            alert("Error: " + data.error);
        }
    });
}
