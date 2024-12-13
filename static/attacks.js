document.addEventListener("DOMContentLoaded", () => {
    // Configura la funcionalidad de la página una vez que se ha cargado el DOM.

    const queryParams = new URLSearchParams(window.location.search);
    const target = queryParams.get("target") || "Ninguno";
    // Obtiene el target desde los parámetros de URL para mostrarlo dinámicamente.

    const bruteBtn = document.getElementById("brute-btn");
    const bruteResults = document.getElementById("brute-results");

    const sqlmapBtn = document.getElementById("sqlmap-btn");
    const sqlmapResults = document.getElementById("sqlmap-results");
    const databaseSelect = document.getElementById("databases-select");
    const executeSqlmapBtn = document.createElement("button");

    executeSqlmapBtn.textContent = "Ejecutar SQLMap en esta base de datos";
    executeSqlmapBtn.style.display = "none"; // Ocultamos el botón inicialmente
    databaseSelect.parentElement.appendChild(executeSqlmapBtn);
    

    const hydraBtn = document.getElementById("hydra-btn");
    const hydraResults = document.getElementById("hydra-results");
    

    // Mostrar el target seleccionado en la UI
    document.getElementById("selected-target").textContent = target;


    bruteBtn.addEventListener("click", () => {
        /*
        Manejador para iniciar el ataque de fuerza bruta.
        - Valida que el usuario haya completado todos los campos del formulario.
        - Envía los datos al servidor para iniciar el ataque.
        - Muestra los resultados en el área de resultados correspondiente.
        */
        // Verificar si no se ha seleccionado un target válido
        if (target === "Ninguno") {
            alert("Por favor, selecciona un target válido.");
            return;
        }

        // Obtener los valores de los campos del formulario
        const loginPath = document.getElementById("web-login-path").value.trim();
        const username = document.getElementById("brute-user").value.trim();
        const userField = document.getElementById("web-user-field").value.trim();
        const passField = document.getElementById("web-pass-field").value.trim();
        const errorMessage = document.getElementById("web-error-message").value.trim();

        // Verificar que todos los campos necesarios estén completos
        if (!loginPath || !username || !userField || !passField || !errorMessage) {
            alert("Por favor, completa todos los campos obligatorios.");
            return;
        }

        // Datos para enviar en la solicitud
        const requestData = {
            target: target,
            login_path: loginPath,
            username: username,
            user_field: userField,
            pass_field: passField,
            error_message: errorMessage
        };

        // Enviar la solicitud al servidor
        fetch('/attacks/bruteforce', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    bruteResults.textContent = `¡Contraseña encontrada! Usuario: ${data.username}, Contraseña: ${data.password}`;
                } else {
                    bruteResults.textContent = data.message || "No se encontró una contraseña válida.";
                }
            })
            .catch(error => {
                bruteResults.textContent = `Error inesperado: ${error.message}`;
                console.error("Error:", error);
            });

    });
    sqlmapBtn.addEventListener("click", () => {
          /*
        Manejador para el ataque SQLMap.
        - Envía datos (URL, atributo) al servidor para buscar bases de datos.
        - Actualiza dinámicamente un select con las bases encontradas.
        */
        const url = document.getElementById("sqlmap-url").value.trim();
        const atributo = document.getElementById("sqlmap-atributo").value.trim();

        if (!url || !atributo) {
            alert("Por favor, completa todos los campos.");
            return;
        }

        sqlmapResults.textContent = "Escaneando...";
        databaseSelect.style.display = "none";
        databaseSelect.innerHTML = '<option value="">Seleccione una base de datos</option>';
        executeSqlmapBtn.style.display = "none";

        fetch('/attacks/sqlmap', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, atributo })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                databaseSelect.style.display = "block";
                data.databases.forEach(db => {
                    const option = document.createElement("option");
                    option.value = db;
                    option.textContent = db;
                    databaseSelect.appendChild(option);
                });
                sqlmapResults.textContent = "Bases de datos encontradas.";
                executeSqlmapBtn.style.display = "inline-block";
            } else {
                sqlmapResults.textContent = data.error || "No se encontraron bases de datos.";
            }
        })
        .catch(error => {
            sqlmapResults.textContent = `Error inesperado: ${error.message}`;
        });
    });

    executeSqlmapBtn.addEventListener("click", () => {
         /*
        Manejador para expandir el ataque SQLMap a una base de datos específica.
        - Envía datos (base seleccionada) al servidor.
        - Muestra resultados extraídos.
        */
        const selectedDatabase = databaseSelect.value;
        const url = document.getElementById("sqlmap-url").value.trim();
        const atributo = document.getElementById("sqlmap-atributo").value.trim();

        if (!selectedDatabase || !url || !atributo) {
            alert("Por favor, selecciona una base de datos y completa los campos requeridos.");
            return;
        }

        sqlmapResults.textContent = `Ejecutando SQLMap en la base de datos: ${selectedDatabase}...`;

        fetch('/attacks/sqlmap/database', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, atributo, database: selectedDatabase })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                sqlmapResults.textContent = `Resultados:\n${data.output}`;
            } else {
                sqlmapResults.textContent = data.error || "Error durante la ejecución de SQLMap.";
            }
        })
        .catch(error => {
            sqlmapResults.textContent = `Error inesperado: ${error.message}`;
        });
    });
    
    hydraBtn.addEventListener("click", () => {
        /*
        Manejador para el ataque Hydra.
        - Valida los datos introducidos por el usuario.
        - Inicia la solicitud al servidor y muestra resultados en el área de resultados.
        */
        // Verificar si no se ha seleccionado un target válido
        if (target === "Ninguno") {
            alert("Por favor, selecciona un target válido.");
            return;
        }

        // Obtener valores del formulario
        const username = document.getElementById("hydra-username").value.trim();
        const scanType = document.querySelector('input[name="hydra-scan-type"]:checked').value;

        if (!username) {
            alert("Por favor, introduce un nombre de usuario.");
            return;
        }

        hydraResults.textContent = "Ejecutando ataque Hydra...";

        // Enviar los datos al servidor
        fetch('/attacks/hydra', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target, username, scanType })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    hydraResults.textContent = `Resultados del ataque:\n${data.output}`;
                } else {
                    hydraResults.textContent = data.error || "Error durante el ataque Hydra.";
                }
            })
            .catch(error => {
                hydraResults.textContent = `Error inesperado: ${error.message}`;
            });
    });
    
});

