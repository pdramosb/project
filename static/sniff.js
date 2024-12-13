document.addEventListener("DOMContentLoaded", () => {
    const startSniffBtn = document.getElementById("start-sniff-btn");
    const stopSniffBtn = document.getElementById("stop-sniff-btn");
    const filterCheckbox = document.getElementById("filter-checkbox");
    const filterIpInput = document.getElementById("filter-ip-input");
    const captureResults = document.getElementById("capture-results");

    // Habilitar/deshabilitar el input de IP basado en el estado del checkbox
    filterCheckbox.addEventListener("change", () => {
        filterIpInput.disabled = !filterCheckbox.checked;
    });

    // Iniciar la captura
    startSniffBtn.addEventListener("click", () => {
        const filterEnabled = filterCheckbox.checked;
        const filterIp = filterIpInput.value.trim();

        captureResults.textContent = "Iniciando captura de paquetes...";
        startSniffBtn.disabled = true;
        stopSniffBtn.disabled = false;

        fetch("/sniff/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filterEnabled, filterIp }),
        })
        .then((response) => response.json())
        .then((data) => {
            if (!data.success) {
                captureResults.textContent = `Error: ${data.error}`;
                startSniffBtn.disabled = false;
                stopSniffBtn.disabled = true;
            } else {
                captureResults.textContent = "Captura en progreso...";
            }
        })
        .catch((error) => {
            captureResults.textContent = `Error inesperado: ${error.message}`;
            startSniffBtn.disabled = false;
            stopSniffBtn.disabled = true;
        });
    });

    // Detener la captura
    stopSniffBtn.addEventListener("click", () => {
        fetch("/sniff/stop", { method: "POST" })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    captureResults.textContent = `Captura detenida.\n\nPaquetes capturados:\n${data.packets}`;
                } else {
                    captureResults.textContent = `Error: ${data.error}`;
                }
                startSniffBtn.disabled = false; // Rehabilitar el botón de inicio
                stopSniffBtn.disabled = true;  // Deshabilitar el botón de detener
            })
            .catch((error) => {
                captureResults.textContent = `Error inesperado: ${error.message}`;
                startSniffBtn.disabled = false;
                stopSniffBtn.disabled = true;
            });
    });

});
