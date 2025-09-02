// Constante para la URL base del proxy
const BASE = "/api";

/**
 * Configuración actualizada para el endpoint de experiencia laboral:
 * - Endpoint: /hoja_vida/reporte_tiempo_experiencia/<numero_documento>
 * - Puerto: 4000 (actualizado desde 5000)
 * - Nueva estructura de respuesta JSON con campos adicionales:
 *   {
 *     "numero_documento": "CC1001",
 *     "reporte_experiencia": [
 *       {
 *         "ocupacion": "SERVIDOR PÚBLICO",
 *         "anios": 2,
 *         "meses": 5,
 *         "total_meses": 29,
 *         "descripcion": "2 años y 5 meses"
 *       }
 *     ]
 *   }
 * - Manejo mejorado de errores: 404 (persona no encontrada), 500 (error de BD)
 * - Categorías incluidas: SERVIDOR PÚBLICO, EMPLEADO DEL SECTOR PRIVADO, 
 *   TRABAJADOR INDEPENDIENTE, TOTAL TIEMPO EXPERIENCIA
 */

// Variables globales para manejo de datos y paginacion
let currentData = [];
let currentPage = 1;
const pageSize = 100;

// Elementos del DOM
const statusArea = document.getElementById('statusArea');
const resultsBody = document.getElementById('resultsBody');
const tableHead = document.getElementById('tableHead');
const paginationContainer = document.getElementById('pagination');

// Botones
const reporteExperienciaBtn = document.getElementById('reporteExperienciaBtn');
const consultarTablaBtn = document.getElementById('consultarTablaBtn');
const healthBtn = document.getElementById('healthBtn');

// Inputs
const numeroDocumentoInput = document.getElementById('numeroDocumento');
const tablaPersonaSelect = document.getElementById('tablaPersona');

// Funcion para mostrar mensajes de estado
function setStatus(message, type = 'info') {
    statusArea.className = `status-message ${type}`;
    statusArea.textContent = message;
}

// Funcion para deshabilitar/habilitar botones
function setButtonsDisabled(disabled) {
    reporteExperienciaBtn.disabled = disabled;
    consultarTablaBtn.disabled = disabled;
    healthBtn.disabled = disabled;
}

// Funcion para crear headers dinamicos basados en los datos
function createDynamicHeaders(data) {
    if (!data || data.length === 0) return;

    const firstRow = data[0];
    const headers = Object.keys(firstRow);

    tableHead.innerHTML = '';
    const headerRow = document.createElement('tr');

    headers.forEach(header => {
        const th = document.createElement('th');
        // Formatear el nombre del header
        th.textContent = header.charAt(0).toUpperCase() + header.slice(1).replace(/_/g, ' ');
        headerRow.appendChild(th);
    });

    tableHead.appendChild(headerRow);
}

// Funcion para renderizar filas en la tabla
function renderRows(data) {
    resultsBody.innerHTML = '';

    if (!data || data.length === 0) {
        const firstRow = tableHead.querySelector('tr');
        const colCount = firstRow ? firstRow.children.length : 1;
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="${colCount}" style="text-align: center; color: #7f8c8d;">No hay resultados para mostrar</td>`;
        resultsBody.appendChild(row);
        return;
    }

    // Crear headers dinamicos si no existen
    if (tableHead.children.length === 0) {
        createDynamicHeaders(data);
    }

    const firstRow = data[0];
    const fields = Object.keys(firstRow);

    data.forEach(item => {
        const row = document.createElement('tr');

        fields.forEach(field => {
            const td = document.createElement('td');
            td.textContent = item[field] || '';
            row.appendChild(td);
        });

        resultsBody.appendChild(row);
    });
}

// Funcion para paginar los datos
function paginate(data, page = 1) {
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedData = data.slice(startIndex, endIndex);

    renderRows(paginatedData);
    renderPagination(data.length, page);
}

// Funcion para renderizar controles de paginacion
function renderPagination(totalItems, page) {
    if (totalItems <= pageSize) {
        paginationContainer.innerHTML = '';
        return;
    }

    const totalPages = Math.ceil(totalItems / pageSize);
    const startItem = ((page - 1) * pageSize) + 1;
    const endItem = Math.min(page * pageSize, totalItems);

    paginationContainer.innerHTML = `
        <div class="pagination-info">
            Mostrando ${startItem} - ${endItem} de ${totalItems} resultados
        </div>
        <div class="pagination-controls">
            <button class="pagination-btn" ${page === 1 ? 'disabled' : ''} onclick="goToPage(${page - 1})">
                Anterior
            </button>
            <span class="pagination-info">Pagina ${page} de ${totalPages}</span>
            <button class="pagination-btn" ${page === totalPages ? 'disabled' : ''} onclick="goToPage(${page + 1})">
                Siguiente
            </button>
        </div>
    `;
}

// Funcion para ir a una pagina especifica
function goToPage(page) {
    currentPage = page;
    paginate(currentData, page);
}

// Funcion para manejar respuestas de la API
async function handleApiResponse(response) {
    if (!response.ok) {
        const errorText = await response.text();
        let errorMessage;

        try {
            const errorJson = JSON.parse(errorText);
            // Manejar códigos de estado específicos
            if (response.status === 404) {
                errorMessage = errorJson.error || errorJson.message || 'No se encontró la persona con el documento proporcionado';
            } else if (response.status === 500) {
                errorMessage = errorJson.error || errorJson.message || 'Error interno del servidor de base de datos';
            } else {
                errorMessage = errorJson.error || errorJson.message || `Error ${response.status}`;
            }
        } catch {
            // Si no se puede parsear como JSON, usar mensajes específicos por código de estado
            if (response.status === 404) {
                errorMessage = 'No se encontró la persona con el documento proporcionado';
            } else if (response.status === 500) {
                errorMessage = 'Error interno del servidor de base de datos';
            } else {
                errorMessage = `Error ${response.status}: ${response.statusText}`;
            }
        }

        throw new Error(errorMessage);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
        return await response.json();
    } else {
        return await response.text();
    }
}

// Funcion para obtener reporte de experiencia laboral
async function fetchReporteExperiencia(numeroDocumento) {
    if (!numeroDocumento || numeroDocumento.trim().length === 0) {
        setStatus('Por favor ingrese un número de documento válido', 'error');
        return;
    }

    try {
        setStatus(`Obteniendo reporte de experiencia para documento: ${numeroDocumento}...`, 'loading');
        setButtonsDisabled(true);

        const encodedDocumento = encodeURIComponent(numeroDocumento.trim());
        const response = await fetch(`${BASE}/hoja_vida/reporte_tiempo_experiencia/${encodedDocumento}`);
        const data = await handleApiResponse(response);

        if (data) {
            // Manejar la nueva estructura de respuesta del API
            // Estructura esperada: {numero_documento: "CC1001", reporte_experiencia: [{ocupacion, anios, meses, total_meses, descripcion}, ...]}
            let arrayData;
            
            if (data.reporte_experiencia && Array.isArray(data.reporte_experiencia)) {
                // Nueva estructura: objeto con numero_documento y reporte_experiencia
                arrayData = data.reporte_experiencia;
                setStatus(`Reporte generado exitosamente para documento: ${data.numero_documento || numeroDocumento}`, 'success');
            } else if (Array.isArray(data)) {
                // Estructura antigua: array directo (mantenida por compatibilidad)
                arrayData = data;
                setStatus(`Reporte generado exitosamente para documento: ${numeroDocumento}`, 'success');
            } else {
                // Estructura de objeto único (mantenida por compatibilidad)
                arrayData = [data];
                setStatus(`Reporte generado exitosamente para documento: ${numeroDocumento}`, 'success');
            }
            
            currentData = arrayData;
            currentPage = 1;

            // Limpiar headers anteriores
            tableHead.innerHTML = '';

            paginate(currentData, currentPage);
        } else {
            currentData = [];
            tableHead.innerHTML = '';
            renderRows([]);
            paginationContainer.innerHTML = '';
            setStatus(`No se encontró información para el documento: ${numeroDocumento}`, 'empty');
        }
    } catch (error) {
        console.error('Error al obtener reporte de experiencia:', error);
        setStatus(`Error al obtener reporte: ${error.message}`, 'error');
        currentData = [];
        tableHead.innerHTML = '';
        renderRows([]);
        paginationContainer.innerHTML = '';
    } finally {
        setButtonsDisabled(false);
    }
}

// Funcion para consultar tabla del sistema
async function fetchTablaPersona(nombreTabla) {
    if (!nombreTabla) {
        setStatus('Por favor seleccione una tabla del sistema', 'error');
        return;
    }

    try {
        setStatus(`Consultando tabla: ${nombreTabla}...`, 'loading');
        setButtonsDisabled(true);

        const response = await fetch(`${BASE}/hoja_vida/tablas_persona/${nombreTabla}`);
        const data = await handleApiResponse(response);

        if (Array.isArray(data) && data.length > 0) {
            currentData = data;
            currentPage = 1;

            // Limpiar headers anteriores
            tableHead.innerHTML = '';

            paginate(currentData, currentPage);
            setStatus(`Se encontraron ${data.length} registros en la tabla ${nombreTabla}`, 'success');
        } else {
            currentData = [];
            tableHead.innerHTML = '';
            renderRows([]);
            paginationContainer.innerHTML = '';
            setStatus(`No se encontraron datos en la tabla: ${nombreTabla}`, 'empty');
        }
    } catch (error) {
        console.error('Error al consultar tabla:', error);
        setStatus(`Error al consultar tabla: ${error.message}`, 'error');
        currentData = [];
        tableHead.innerHTML = '';
        renderRows([]);
        paginationContainer.innerHTML = '';
    } finally {
        setButtonsDisabled(false);
    }
}

// Funcion para verificar el estado de la API
async function pingHealth() {
    try {
        setStatus('Verificando estado de la API...', 'loading');
        setButtonsDisabled(true);

        const response = await fetch(`${BASE}/health`);
        const data = await handleApiResponse(response);

        // Limpiar tabla ya que health no devuelve datos tabulares
        currentData = [];
        tableHead.innerHTML = '';
        renderRows([]);
        paginationContainer.innerHTML = '';

        if (response.ok) {
            setStatus('API funcionando correctamente', 'success');
        } else {
            setStatus(`API respondió con estado: ${response.status}`, 'error');
        }
    } catch (error) {
        console.error('Error al verificar health:', error);
        setStatus(`Error al verificar estado de la API: ${error.message}`, 'error');
        currentData = [];
        tableHead.innerHTML = '';
        renderRows([]);
        paginationContainer.innerHTML = '';
    } finally {
        setButtonsDisabled(false);
    }
}

// Funcion para validar input de texto
function validateTextInput(input) {
    const value = input.value.trim();
    if (value.length === 0) {
        input.style.borderColor = '#e74c3c';
        return false;
    } else {
        input.style.borderColor = '#ddd';
        return true;
    }
}

// Funcion para validar select
function validateSelect(select) {
    if (!select.value) {
        select.style.borderColor = '#e74c3c';
        return false;
    } else {
        select.style.borderColor = '#ddd';
        return true;
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function () {
    // Evento para reporte de experiencia
    reporteExperienciaBtn.addEventListener('click', function () {
        const numeroDocumento = numeroDocumentoInput.value.trim();
        if (validateTextInput(numeroDocumentoInput)) {
            fetchReporteExperiencia(numeroDocumento);
        }
    });

    // Evento para consultar tabla
    consultarTablaBtn.addEventListener('click', function () {
        const nombreTabla = tablaPersonaSelect.value;
        if (validateSelect(tablaPersonaSelect)) {
            fetchTablaPersona(nombreTabla);
        }
    });

    // Evento para health check
    healthBtn.addEventListener('click', pingHealth);

    // Validacion en tiempo real de inputs
    numeroDocumentoInput.addEventListener('input', function () {
        validateTextInput(this);
    });

    tablaPersonaSelect.addEventListener('change', function () {
        validateSelect(this);
    });

    // Permitir envio con Enter en el input
    numeroDocumentoInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            reporteExperienciaBtn.click();
        }
    });

    // Mensaje inicial
    setStatus('Seleccione una operación para comenzar', 'info');
});
