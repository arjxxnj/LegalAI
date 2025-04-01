document.addEventListener('DOMContentLoaded', function() {
    // Form validation for case submission
    const caseForm = document.getElementById('caseForm');
    if (caseForm) {
        caseForm.addEventListener('submit', function(event) {
            const requiredFields = [
                'name', 'email', 'case_type', 'offense_description', 'query'
            ];
            
            let formIsValid = true;
            
            // Check required fields
            requiredFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (!field.value.trim()) {
                    formIsValid = false;
                    field.classList.add('is-invalid');
                    
                    // Create error message if it doesn't exist
                    let errorDiv = field.nextElementSibling;
                    if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                        errorDiv = document.createElement('div');
                        errorDiv.className = 'invalid-feedback';
                        errorDiv.textContent = 'This field is required';
                        field.parentNode.insertBefore(errorDiv, field.nextSibling);
                    }
                } else {
                    field.classList.remove('is-invalid');
                    
                    // Remove error message if it exists
                    const errorDiv = field.nextElementSibling;
                    if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                        errorDiv.remove();
                    }
                }
            });
            
            // Validate email format
            const emailField = document.getElementById('email');
            if (emailField && emailField.value.trim()) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(emailField.value.trim())) {
                    formIsValid = false;
                    emailField.classList.add('is-invalid');
                    
                    // Create or update error message
                    let errorDiv = emailField.nextElementSibling;
                    if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                        errorDiv = document.createElement('div');
                        errorDiv.className = 'invalid-feedback';
                        emailField.parentNode.insertBefore(errorDiv, emailField.nextSibling);
                    }
                    errorDiv.textContent = 'Please enter a valid email address';
                }
            }
            
            // Prevent form submission if validation fails
            if (!formIsValid) {
                event.preventDefault();
                
                // Scroll to the first error
                const firstError = document.querySelector('.is-invalid');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            } else {
                // Show loading spinner
                const spinnerContainer = document.querySelector('.spinner-container');
                if (spinnerContainer) {
                    spinnerContainer.style.display = 'block';
                }
                
                // Disable submit button to prevent double submission
                const submitBtn = caseForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                }
            }
        });
        
        // Reset validation on input
        caseForm.querySelectorAll('input, textarea, select').forEach(field => {
            field.addEventListener('input', function() {
                this.classList.remove('is-invalid');
                const errorDiv = this.nextElementSibling;
                if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                    errorDiv.remove();
                }
            });
        });
    }
    
    // Collapsible sections in analysis view
    const collapsibleButtons = document.querySelectorAll('.btn-toggle-section');
    if (collapsibleButtons) {
        collapsibleButtons.forEach(button => {
            button.addEventListener('click', function() {
                const targetId = this.getAttribute('data-bs-target');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    const isExpanded = this.getAttribute('aria-expanded') === 'true';
                    this.setAttribute('aria-expanded', !isExpanded);
                    
                    if (isExpanded) {
                        targetElement.classList.add('collapse');
                        this.querySelector('.toggle-icon').classList.remove('bi-chevron-up');
                        this.querySelector('.toggle-icon').classList.add('bi-chevron-down');
                    } else {
                        targetElement.classList.remove('collapse');
                        this.querySelector('.toggle-icon').classList.remove('bi-chevron-down');
                        this.querySelector('.toggle-icon').classList.add('bi-chevron-up');
                    }
                }
            });
        });
    }
    
    // Case type selection affects form fields visibility
    const caseTypeSelect = document.getElementById('case_type');
    if (caseTypeSelect) {
        caseTypeSelect.addEventListener('change', function() {
            const selectedType = this.value;
            
            // Show/hide victim details field for certain case types
            const victimDetailsGroup = document.getElementById('victim_details_group');
            if (victimDetailsGroup) {
                if (['Assault', 'Murder', 'Rape', 'Domestic Violence'].includes(selectedType)) {
                    victimDetailsGroup.classList.remove('d-none');
                    document.getElementById('victim_details').setAttribute('required', 'required');
                } else {
                    victimDetailsGroup.classList.add('d-none');
                    document.getElementById('victim_details').removeAttribute('required');
                }
            }
            
            // Update query placeholder based on case type
            const queryField = document.getElementById('query');
            if (queryField) {
                const placeholderMap = {
                    'Theft': 'Example: I need to understand what charges can be filed for a stolen mobile phone from my shop...',
                    'Assault': 'Example: My neighbor attacked me during an argument and I suffered minor injuries...',
                    'Fraud': 'Example: I paid for services that were never delivered despite multiple follow-ups...',
                    'Murder': 'Example: I need to understand the legal implications in a case where someone was killed during a fight...',
                    'Rape': 'Example: I need to understand the legal process for reporting a sexual assault case...',
                    'Domestic Violence': 'Example: I am suffering abuse from my spouse and need to know my legal options...',
                    'Cybercrime': 'Example: Someone is using my pictures online without permission and harassing me...'
                };
                
                queryField.placeholder = placeholderMap[selectedType] || 'Please describe your legal query in detail...';
            }
        });
    }
    
    // Initialize tooltips and popovers
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Format analysis content
    const analysisContent = document.querySelector('.analysis-content');
    if (analysisContent) {
        // Convert markdown-like content to HTML
        let content = analysisContent.innerHTML;
        
        // Convert headers
        content = content.replace(/## (.*)/g, '<h2>$1</h2>');
        content = content.replace(/### (.*)/g, '<h3>$1</h3>');
        content = content.replace(/#### (.*)/g, '<h4>$1</h4>');
        
        // Convert bold text
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert lists (simple implementation)
        content = content.replace(/^\d\. (.*)/gm, '<ol><li>$1</li></ol>');
        
        // Apply the formatted content
        analysisContent.innerHTML = content;
        
        // Fix consecutive list items
        const lists = analysisContent.querySelectorAll('ol');
        lists.forEach(list => {
            const nextEl = list.nextElementSibling;
            if (nextEl && nextEl.tagName === 'OL') {
                // Move the li from the next list to this one
                const items = nextEl.querySelectorAll('li');
                items.forEach(item => {
                    list.appendChild(item.cloneNode(true));
                });
                nextEl.remove();
            }
        });
    }
});
