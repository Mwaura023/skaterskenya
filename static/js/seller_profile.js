document.addEventListener('DOMContentLoaded', function() {
    // Initialize Select2
    $('.select2-multiple').select2({
        placeholder: "Select product categories",
        allowClear: true,
        width: '100%',
        theme: 'bootstrap-5'
    });

    // Form validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill all required fields');
            }
        });
    }
});