
// Enable all tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add click-to-copy functionality
    document.querySelectorAll('.copy-text').forEach(element => {
        element.addEventListener('click', function() {
            navigator.clipboard.writeText(this.textContent).then(() => {
                // Show feedback
                this.classList.add('copied');
                setTimeout(() => this.classList.remove('copied'), 1000);
            });
        });
    });

    // Add section highlighting
    document.querySelectorAll('.analysis-section').forEach(section => {
        section.addEventListener('click', function() {
            document.querySelectorAll('.analysis-section').forEach(s => 
                s.classList.remove('active-section'));
            this.classList.add('active-section');
        });
    });

    // Initialize floating action button
    const fab = document.querySelector('.floating-action');
    if (fab) {
        window.onscroll = function() {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                fab.style.display = "block";
            } else {
                fab.style.display = "none";
            }
        };
    }

    // Add evidence tag filtering
    document.querySelectorAll('.evidence-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            const evidenceType = this.dataset.evidence;
            document.querySelectorAll('.evidence-item').forEach(item => {
                if (item.dataset.evidenceType === evidenceType) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
});

// Print function with custom styling
function printAnalysis() {
    window.print();
}

// Scroll to section function
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}
