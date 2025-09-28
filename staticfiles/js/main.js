// Main JavaScript for Offline Recruitment System

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeFormValidation();
    initializeSearchFilters();
    initializeBulkActions();
    initializeImagePreview();
    initializeTooltips();
});

// Form validation enhancement
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    });
}

// Validate individual fields
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    let isValid = true;
    let errorMessage = '';

    // Clear previous validation
    field.classList.remove('is-valid', 'is-invalid');
    const feedback = field.parentNode.querySelector('.invalid-feedback');
    if (feedback) feedback.remove();

    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required.';
    }

    // Email validation
    if (fieldName === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address.';
        }
    }

    // Phone validation
    if (fieldName === 'phone_number' && value) {
        const phoneRegex = /^[\+]?[1-9][\d\s\-\(\)]{7,15}$/;
        if (!phoneRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid phone number.';
        }
    }

    // Age validation
    if (fieldName === 'birth_date' && value) {
        const birthDate = new Date(value);
        const today = new Date();
        const age = today.getFullYear() - birthDate.getFullYear();

        if (age < 16 || age > 100) {
            isValid = false;
            errorMessage = 'Age must be between 16 and 100 years.';
        }
    }

    // Apply validation styling
    if (isValid) {
        field.classList.add('is-valid');
    } else {
        field.classList.add('is-invalid');
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'invalid-feedback';
        feedbackDiv.textContent = errorMessage;
        field.parentNode.appendChild(feedbackDiv);
    }

    return isValid;
}

// Validate entire form
function validateForm(form) {
    const fields = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isFormValid = true;

    fields.forEach(field => {
        if (!validateField(field)) {
            isFormValid = false;
        }
    });

    return isFormValid;
}

// Search and filter functionality
function initializeSearchFilters() {
    const searchForm = document.querySelector('.search-filters form');
    if (!searchForm) return;

    const searchInput = searchForm.querySelector('input[name="search_query"]');
    const filterSelects = searchForm.querySelectorAll('select');

    // Auto-submit on filter change
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            searchForm.submit();
        });
    });

    // Search suggestions (if API is available)
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                showSearchSuggestions(this.value);
            }, 300);
        });
    }

    // Clear filters button
    const clearButton = document.createElement('button');
    clearButton.type = 'button';
    clearButton.className = 'btn btn-secondary btn-sm';
    clearButton.textContent = 'Clear Filters';
    clearButton.addEventListener('click', clearFilters);

    const filterRow = searchForm.querySelector('.filter-row');
    if (filterRow) {
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'd-flex align-items-end';
        buttonContainer.appendChild(clearButton);
        filterRow.appendChild(buttonContainer);
    }
}

// Clear all filters
function clearFilters() {
    const form = document.querySelector('.search-filters form');
    if (!form) return;

    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.type === 'text' || input.type === 'number' || input.type === 'email') {
            input.value = '';
        } else if (input.tagName === 'SELECT') {
            input.selectedIndex = 0;
        }
    });

    form.submit();
}

// Show search suggestions
function showSearchSuggestions(query) {
    if (query.length < 2) return;

    // This would typically make an API call
    // For offline mode, we can implement local search if needed
    console.log('Search suggestions for:', query);
}

// Bulk actions functionality
function initializeBulkActions() {
    const selectAllCheckbox = document.querySelector('#select-all');
    const candidateCheckboxes = document.querySelectorAll('.candidate-checkbox');
    const bulkActionForm = document.querySelector('#bulk-action-form');
    const actionSelect = document.querySelector('#bulk-action-select');

    if (!selectAllCheckbox || !candidateCheckboxes.length) return;

    // Select/deselect all
    selectAllCheckbox.addEventListener('change', function() {
        candidateCheckboxes.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
        updateBulkActionButton();
    });

    // Individual checkbox changes
    candidateCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectAllState();
            updateBulkActionButton();
        });
    });

    // Bulk action form submission
    if (bulkActionForm && actionSelect) {
        bulkActionForm.addEventListener('submit', function(e) {
            const selectedCheckboxes = document.querySelectorAll('.candidate-checkbox:checked');
            const action = actionSelect.value;

            if (!action) {
                e.preventDefault();
                alert('Please select an action.');
                return;
            }

            if (selectedCheckboxes.length === 0) {
                e.preventDefault();
                alert('Please select at least one candidate.');
                return;
            }

            if (action === 'delete') {
                if (!confirm(`Are you sure you want to delete ${selectedCheckboxes.length} candidate(s)?`)) {
                    e.preventDefault();
                    return;
                }
            }

            // Add selected IDs to hidden input
            const selectedIds = Array.from(selectedCheckboxes).map(cb => cb.value);
            let hiddenInput = document.querySelector('#selected-candidates');
            if (!hiddenInput) {
                hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'selected_candidates';
                hiddenInput.id = 'selected-candidates';
                this.appendChild(hiddenInput);
            }
            hiddenInput.value = selectedIds.join(',');
        });
    }
}

// Update select all checkbox state
function updateSelectAllState() {
    const selectAllCheckbox = document.querySelector('#select-all');
    const candidateCheckboxes = document.querySelectorAll('.candidate-checkbox');
    const checkedCount = document.querySelectorAll('.candidate-checkbox:checked').length;

    if (checkedCount === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    } else if (checkedCount === candidateCheckboxes.length) {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.indeterminate = false;
    } else {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = true;
    }
}

// Update bulk action button state
function updateBulkActionButton() {
    const bulkActionButton = document.querySelector('#bulk-action-button');
    const checkedCount = document.querySelectorAll('.candidate-checkbox:checked').length;

    if (bulkActionButton) {
        bulkActionButton.disabled = checkedCount === 0;
        bulkActionButton.textContent = checkedCount > 0 ?
            `Bulk Actions (${checkedCount})` : 'Bulk Actions';
    }
}

// Image preview functionality
function initializeImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');

    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            previewImage(this);
        });
    });
}

// Preview selected image
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            let preview = document.querySelector('#image-preview');

            if (!preview) {
                preview = document.createElement('div');
                preview.id = 'image-preview';
                preview.className = 'mt-2';
                input.parentNode.appendChild(preview);
            }

            preview.innerHTML = `
                <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 8px; border: 2px solid #dee2e6;">
                <button type="button" class="btn btn-sm btn-danger mt-1 d-block" onclick="clearImagePreview()">Remove</button>
            `;
        };

        reader.readAsDataURL(input.files[0]);
    }
}

// Clear image preview
function clearImagePreview() {
    const preview = document.querySelector('#image-preview');
    const input = document.querySelector('input[type="file"][accept*="image"]');

    if (preview) preview.remove();
    if (input) input.value = '';
}

// Initialize tooltips and help text
function initializeTooltips() {
    // Add help text for complex fields
    const helpTexts = {
        'birth_date': 'Candidate must be at least 16 years old',
        'phone_number': 'Include country code (e.g., +1234567890)',
        'email': 'Must be unique across all candidates'
    };

    Object.keys(helpTexts).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field && !field.parentNode.querySelector('.form-text')) {
            const helpDiv = document.createElement('small');
            helpDiv.className = 'form-text text-muted';
            helpDiv.textContent = helpTexts[fieldName];
            field.parentNode.appendChild(helpDiv);
        }
    });
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;

    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Age calculator utility
function calculateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
    }

    return age;
}

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for global access
window.showAlert = showAlert;
window.clearImagePreview = clearImagePreview;
window.calculateAge = calculateAge;
