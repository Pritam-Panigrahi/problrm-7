function validatePhoneNumber(phone) {
    const cleaned = phone.replace(/\D/g, '');
    const pattern = /^[6-9]\d{9}$/;
    return pattern.test(cleaned);
}

function validateEmail(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}

function sanitizeInput(input) {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
}
