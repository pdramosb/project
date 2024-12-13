document.addEventListener("DOMContentLoaded", () => {
// Inicializar referencias a los elementos del DOM
    const scanBtn = document.getElementById("scan-btn");
    const ipSelect = document.getElementById("ip-select");
    const arpResults = document.getElementById("arp-results");
    const selectedTarget = document.getElementById("selected-target");
    const nmapBtn = document.getElementById("nmap-btn");
    const nmapResults = document.getElementById("nmap-results");
    const fuzzBtn = document.getElementById("fuzz-btn");
    const fuzzUrl = document.getElementById("fuzz-url");
    const fuzzResults = document.getElementById("fuzz-results");
    const dictionaryInput = document.getElementById("dictionary");
    const checkboxes = ["html", "txt", "php"];

    // Recuperar el target desde la URL y mostrarlo
    const queryParams = new URLSearchParams(window.location.search);
    const savedTarget = queryParams.get("target") || "Ninguno";
    selectedTarget.textContent = savedTarget;

    // Cuando el usuario seleccione una IP
    ipSelect.addEventListener("change", (event) => {
        const selectedIp = event.target.value;
        if (selectedIp) {
            // Actualizamos la URL con el nuevo target
            const newUrl = `${window.location.pathname}?target=${encodeURIComponent(selectedIp)}`;
            window.location.href = newUrl;
        }
    });

    // Escaneo ARP para llenar el desplegable y la lista
    scanBtn.addEventListener("click", () => {
        fetch('/scans', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                ipSelect.innerHTML = '<option value="">--Seleccione una IP--</option>';
                arpResults.textContent = ""; // Limpiar resultados previos

                if (data.ips) {
                    data.ips.forEach(entry => {
                        const [ip, mac] = entry.split("\t");
                        // Agregar al desplegable
                        const option = document.createElement("option");
                        option.value = ip;
                        option.textContent = ip;
                        ipSelect.appendChild(option);

                        // Agregar entrada al contenido de arp-results
                        arpResults.textContent += `${ip} (${mac || "MAC desconocida"})\n`;
                    });
                }
            })
            .catch(error => console.error('Error:', error));
    });


      // Escaneo Nmap, habilitado solo si se selecciona un target válido
    nmapBtn.disabled = (savedTarget === "Ninguno");
    nmapBtn.addEventListener("click", () => {
        if (savedTarget !== "Ninguno") {
            fetch(`/scans/nmap`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ip: savedTarget })
            })
                .then(response => response.json())
                .then(data => {
                    nmapResults.textContent = data.results || "Escaneo completado.";
                })
                .catch(error => console.error('Error:', error));
        }
    });
    // Habilitar botón de Fuzzing cuando haya una URL válida
    fuzzUrl.addEventListener("input", () => {
        fuzzBtn.disabled = !fuzzUrl.value.trim();
    });

    // Botón de Fuzzing
    fuzzBtn.addEventListener("click", () => {
        const url = fuzzUrl.value.trim();
        if (!url) return alert("Por favor, introduce una URL válida.");

        // Obtener los valores de los checkboxes
        const selectedExtensions = checkboxes
            .filter(id => document.getElementById(id).checked)
            .map(id => document.getElementById(id).value)
            .join(',');

        // Crear el objeto de datos
        const formData = new FormData();
        formData.append("url", url);
        formData.append("extensions", selectedExtensions);
        if (dictionaryInput.files[0]) {
            formData.append("dictionary", dictionaryInput.files[0]);
        }

        // Enviar los datos al backend
        fetch('/scans/fuzzing', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                fuzzResults.textContent = data.results || "Fuzzing completado.";
            })
            .catch(error => console.error('Error:', error));
    });
});

