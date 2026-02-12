// Sistema de Inventario - Scripts principales

$(document).ready(function() {
    // Inicializar DataTables
    if ($('.datatable').length) {
        $('.datatable').DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/es-ES.json'
            },
            pageLength: 25,
            responsive: true,
            order: [[0, 'desc']]
        });
    }
    
    // Inicializar Select2
    if ($('.select2').length) {
        $('.select2').select2({
            theme: 'bootstrap-5',
            width: '100%'
        });
    }
    
    // Auto-cerrar alertas después de 5 segundos
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Confirmar eliminación
    $('.btn-delete').on('click', function(e) {
        e.preventDefault();
        const url = $(this).data('url');
        const message = $(this).data('message') || '¿Está seguro de eliminar este registro?';
        
        Swal.fire({
            title: 'Confirmar eliminación',
            text: message,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#e74a3b',
            cancelButtonColor: '#858796',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = url;
            }
        });
    });
    
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Validación de formularios en tiempo real
    $('form').on('submit', function() {
        $(this).find('button[type="submit"]').prop('disabled', true);
        $(this).find('.btn-submit').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...');
    });
});

// Función para formatear moneda
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP'
    }).format(amount);
}

// Función para formatear fecha
function formatDate(date) {
    return new Intl.DateTimeFormat('es-CL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// Función para copiar al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        Swal.fire({
            icon: 'success',
            title: 'Copiado',
            text: 'Texto copiado al portapapeles',
            timer: 1500,
            showConfirmButton: false
        });
    }).catch(function(err) {
        console.error('Error al copiar: ', err);
    });
}

// Función para exportar tabla a Excel
function exportToExcel(tableId, filename) {
    const table = document.getElementById(tableId);
    const wb = XLSX.utils.table_to_book(table, {sheet: "Sheet1"});
    XLSX.writeFile(wb, `${filename}.xlsx`);
}

// Función para exportar a PDF
function exportToPDF(elementId, filename) {
    const element = document.getElementById(elementId);
    html2pdf().set({
        margin: 1,
        filename: `${filename}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    }).from(element).save();
}

// Sistema de notificaciones
class NotificationService {
    static showSuccess(message) {
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            text: message,
            timer: 3000,
            showConfirmButton: false
        });
    }
    
    static showError(message) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: message,
            confirmButtonColor: '#e74a3b'
        });
    }
    
    static showWarning(message) {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: message,
            confirmButtonColor: '#f6c23e'
        });
    }
    
    static showInfo(message) {
        Swal.fire({
            icon: 'info',
            title: 'Información',
            text: message,
            confirmButtonColor: '#36b9cc'
        });
    }
}

// Sistema de búsqueda en vivo
class LiveSearch {
    constructor(inputId, tableId) {
        this.input = document.getElementById(inputId);
        this.table = document.getElementById(tableId);
        this.rows = this.table.querySelectorAll('tbody tr');
        this.init();
    }
    
    init() {
        this.input.addEventListener('keyup', () => this.search());
    }
    
    search() {
        const query = this.input.value.toLowerCase();
        
        this.rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
        });
    }
}

// Exportar funciones globales
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.copyToClipboard = copyToClipboard;
window.exportToExcel = exportToExcel;
window.exportToPDF = exportToPDF;
window.NotificationService = NotificationService;
window.LiveSearch = LiveSearch;