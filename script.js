// Simple JavaScript interactivity

function showModal() {
    document.getElementById('modal').classList.remove('hidden');
    document.getElementById('modal').classList.add('flex');
}

function hideModal() {
    const modal = document.getElementById('modal');
    modal.classList.remove('flex');
    modal.classList.add('hidden');
}

// Basic contact form handler (placeholder for now)
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('contact-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Thank you! This form is a placeholder — we can connect it to real functionality later.');
            hideModal();
            form.reset();
        });
    }

    // Optional: Close modal when clicking outside
    const modal = document.getElementById('modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                hideModal();
            }
        });
    }
});

// Future enhancements can go here (theme toggle, smooth scroll, etc.)
console.log('Website script loaded successfully.');
