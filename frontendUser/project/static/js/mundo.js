// Constante para la URL base del proxy
const BASE = "/api";

// Variables globales para manejo de datos y paginacion
// Los datos de la API contienen: {country, state, city}
let currentData = [];
let currentPage = 1;
const pageSize = 100;

// Elementos del DOM
const statusArea = document.getElementById('statusArea');
const resultsBody = document.getElementById('resultsBody');
const paginationContainer = document.getElementById('pagination');

// Botones
const loadAllBtn = document.getElementById('loadAllBtn');
const filterByCountryBtn = document.getElementById('filterByCountryBtn');
const duplicatesBtn = document.getElementById('duplicatesBtn');
const healthBtn = document.getElementById('healthBtn');

// Inputs
const countryNameInput = document.getElementById('countryName');
const countryNameDupInput = document.getElementById('countryNameDup');

// Funcion para mostrar mensajes de estado
function setStatus(message, type = 'info') {
    statusArea.className = `status-message ${type}`;
    statusArea.textContent = message;
}

// Funcion para deshabilitar/habilitar botones
function setButtonsDisabled(disabled) {
    loadAllBtn.disabled = disabled;
    filterByCountryBtn.disabled = disabled;
    duplicatesBtn.disabled = disabled;
    healthBtn.disabled = disabled;
}

// Funcion para renderizar filas en la tabla
function renderRows(data) {
    resultsBody.innerHTML = '';

    if (!data || data.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="3" style="text-align: center; color: #7f8c8d;">No hay resultados para mostrar</td>';
        resultsBody.appendChild(row);
        return;
    }

    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.country || ''}</td>
            <td>${item.state || ''}</td>
            <td>${item.city || ''}</td>
        `;
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
            errorMessage = errorJson.error || errorJson.message || `Error ${response.status}`;
        } catch {
            errorMessage = `Error ${response.status}: ${response.statusText}`;
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

// Funcion para cargar todos los datos
async function fetchAll() {
    try {
        setStatus('Cargando todos los paises, estados y ciudades...', 'loading');
        setButtonsDisabled(true);

        const response = await fetch(`${BASE}/mundo/obtenerPaisesEstadosCiudades`);
        const data = await handleApiResponse(response);

        if (Array.isArray(data) && data.length > 0) {
            currentData = data;
            currentPage = 1;
            paginate(currentData, currentPage);
            setStatus(`Se cargaron ${data.length} registros exitosamente`, 'success');
        } else {
            currentData = [];
            renderRows([]);
            paginationContainer.innerHTML = '';
            setStatus('No se encontraron datos', 'empty');
        }
    } catch (error) {
        console.error('Error al cargar todos los datos:', error);
        setStatus(`Error al cargar datos: ${error.message}`, 'error');
        currentData = [];
        renderRows([]);
        paginationContainer.innerHTML = '';
    } finally {
        setButtonsDisabled(false);
    }
}

// Funcion para filtrar por pais
async function fetchByCountry(countryName) {
    if (!countryName || countryName.trim().length === 0) {
        setStatus('Por favor ingrese un nombre de pais valido', 'error');
        return;
    }

    try {
        setStatus(`Filtrando por pais: ${countryName}...`, 'loading');
        setButtonsDisabled(true);

        // Codificar el nombre del pais para la URL
        const encodedCountryName = encodeURIComponent(countryName.trim());
        const response = await fetch(`${BASE}/obtenerPaisesEstadosCiudades/${encodedCountryName}`);
        const data = await handleApiResponse(response);

        if (Array.isArray(data) && data.length > 0) {
            currentData = data;
            currentPage = 1;
            paginate(currentData, currentPage);
            setStatus(`Se encontraron ${data.length} registros para el pais: ${countryName}`, 'success');
        } else {
            currentData = [];
            renderRows([]);
            paginationContainer.innerHTML = '';
            setStatus(`No se encontraron datos para el pais: ${countryName}`, 'empty');
        }
    } catch (error) {
        console.error('Error al filtrar por pais:', error);
        setStatus(`Error al filtrar por pais: ${error.message}`, 'error');
        currentData = [];
        renderRows([]);
        paginationContainer.innerHTML = '';
    } finally {
        setButtonsDisabled(false);
    }
}

// Funcion para obtener ciudades repetidas
async function fetchDuplicates(countryName) {
    if (!countryName || countryName.trim().length === 0) {
        setStatus('Por favor ingrese un nombre de pais valido', 'error');
        return;
    }

    try {
        setStatus(`Buscando ciudades repetidas en pais: ${countryName}...`, 'loading');
        setButtonsDisabled(true);

        // Codificar el nombre del pais para la URL
        const encodedCountryName = encodeURIComponent(countryName.trim());
        const response = await fetch(`${BASE}/listarCiudadesRepetidasPais/${encodedCountryName}`);
        const data = await handleApiResponse(response);

        if (Array.isArray(data) && data.length > 0) {
            currentData = data;
            currentPage = 1;
            paginate(currentData, currentPage);
            setStatus(`Se encontraron ${data.length} ciudades repetidas en el pais: ${countryName}`, 'success');
        } else {
            currentData = [];
            renderRows([]);
            paginationContainer.innerHTML = '';
            setStatus(`No se encontraron ciudades repetidas en el pais: ${countryName}`, 'empty');
        }
    } catch (error) {
        console.error('Error al buscar ciudades repetidas:', error);
        setStatus(`Error al buscar ciudades repetidas: ${error.message}`, 'error');
        currentData = [];
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
        renderRows([]);
        paginationContainer.innerHTML = '';

        if (response.ok) {
            setStatus('API funcionando correctamente', 'success');
        } else {
            setStatus(`API respondio con estado: ${response.status}`, 'error');
        }
    } catch (error) {
        console.error('Error al verificar health:', error);
        setStatus(`Error al verificar estado de la API: ${error.message}`, 'error');
        currentData = [];
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

// Event listeners
document.addEventListener('DOMContentLoaded', function () {
    // Evento para cargar todos los datos
    loadAllBtn.addEventListener('click', fetchAll);

    // Evento para filtrar por pais
    filterByCountryBtn.addEventListener('click', function () {
        const countryName = countryNameInput.value.trim();
        if (validateTextInput(countryNameInput)) {
            fetchByCountry(countryName);
        }
    });

    // Evento para buscar ciudades repetidas
    duplicatesBtn.addEventListener('click', function () {
        const countryName = countryNameDupInput.value.trim();
        if (validateTextInput(countryNameDupInput)) {
            fetchDuplicates(countryName);
        }
    });

    // Evento para health check
    healthBtn.addEventListener('click', pingHealth);

    // Validacion en tiempo real de inputs
    countryNameInput.addEventListener('input', function () {
        validateTextInput(this);
    });

    countryNameDupInput.addEventListener('input', function () {
        validateTextInput(this);
    });

    // Permitir envio con Enter en los inputs
    countryNameInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            filterByCountryBtn.click();
        }
    });

    countryNameDupInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            duplicatesBtn.click();
        }
    });

    // Mensaje inicial
    setStatus('Seleccione una operacion para comenzar', 'info');
});
