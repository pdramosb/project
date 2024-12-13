// Espera a que el contenido del DOM esté completamente cargado
document.addEventListener("DOMContentLoaded", () => {
    // Selecciona todos los botones con la clase "save-btn" y agrega un evento de clic a cada uno
    document.querySelectorAll(".save-btn").forEach(button => {
        button.addEventListener("click", () => {
            // Obtiene el atributo "data-target" del botón, que identifica el elemento objetivo
            const targetId = button.getAttribute("data-target");
            const targetElement = document.getElementById(targetId);

            // Verifica si el elemento objetivo existe
            if (!targetElement) {
                alert("Elemento objetivo no encontrado."); // Muestra una alerta si no se encuentra el elemento
                return;
            }

            // Obtiene el contenido del elemento objetivo y elimina espacios en blanco
            const content = targetElement.textContent.trim();
            // Verifica si hay contenido disponible para guardar
            if (!content) {
                alert("No hay datos para guardar."); // Muestra una alerta si no hay contenido
                return;
            }

            // Envía el contenido al servidor mediante una solicitud POST
            fetch('/save-results', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }, // Especifica el formato JSON
                body: JSON.stringify({ content }) // Incluye el contenido en el cuerpo de la solicitud
            })
                .then(response => response.json()) // Procesa la respuesta como JSON
                .then(data => {
                    // Verifica si el servidor confirmó que la operación fue exitosa
                    if (data.success) {
                        alert("Datos guardados exitosamente."); // Muestra un mensaje de éxito
                    } else {
                        alert("Error al guardar datos: " + data.error); // Muestra un mensaje de error si falla
                    }
                })
                .catch(error => console.error('Error:', error)); // Maneja errores en la solicitud
        });
    });
});

