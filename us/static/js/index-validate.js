function validatePassword() {
    // Get the value of the password input
    const passwordInput = document.getElementById('password').value;
    const passwordError = document.getElementById('password-error');
    
    // If password is empty, no validation needed
    if (!passwordInput) {
        passwordError.textContent = '';
        passwordError.classList.add('hidden');
        return true;
    }

    // Check if the password meets the requirements
    if (passwordInput.length < 4) {
        // Display an error message if the password is too short
        passwordError.textContent = 'Password must be at least 4 characters long';
        passwordError.classList.remove('hidden');
        
        // Show the advanced options if there's a password error
        const advancedOptions = document.getElementById('advanced-options');
        const advancedToggle = document.getElementById('advanced-options-toggle');
        if (advancedOptions && !advancedOptions.classList.contains('show')) {
            advancedOptions.classList.add('show');
            advancedOptions.classList.remove('hidden');
            if (advancedToggle) {
                advancedToggle.classList.add('active');
            }
        }
        
        return false;
    }

    // Clear any error message
    passwordError.textContent = '';
    passwordError.classList.add('hidden');
    return true;
}

function validateURL() {
    // Get the value of the long URL input
    const longUrlInput = document.getElementById('long-url').value;
    const urlError = document.getElementById('url-error');

    // Check if the URL is valid using a regular expression
    const regex = /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/i;

    if (!regex.test(longUrlInput)) {
        // Display an error message if the URL is invalid
        urlError.textContent = 'Please enter a valid URL (e.g., https://example.com)';
        urlError.classList.remove('hidden');
        return false;
    }

    // Clear any error message
    urlError.textContent = '';
    urlError.classList.add('hidden');
    return true;
}

// Custom Time Expiration is currently Buggy and not ready for Production

// function validateExpiration() {
//     var expiration = document.getElementById("expiration-time").value;

//     if (expiration.trim() === "") {
//         return true;
//     }

//     var expirationDate = new Date(expiration);
//     var currentDate = new Date();
//     var diff = expirationDate - currentDate;
//     console.log(diff);

//     if (diff < 540000) {
//         customTopNotification("ExpirationError", "Expiration date must be at least 10 minutes from now", 10);
//         return false;
//     }

//     return true;
// }

// Add event listeners to validate in real-time
document.addEventListener('DOMContentLoaded', function() {
    const longUrlInput = document.getElementById('long-url');
    const passwordInput = document.getElementById('password');
    
    if (longUrlInput) {
        longUrlInput.addEventListener('input', validateURL);
    }
    
    if (passwordInput) {
        passwordInput.addEventListener('input', validatePassword);
    }
});

function validateFormSubmission() {
    // Validate URL first
    const isUrlValid = validateURL();
    
    // If URL is invalid, return false to prevent form submission
    if (!isUrlValid) {
        return false;
    }
    
    // Check if advanced options are being used
    const advancedOptions = document.getElementById('advanced-options');
    const passwordInput = document.getElementById('password');
    const aliasInput = document.getElementById('alias');
    const maxClicksInput = document.getElementById('max-clicks');
    
    // If any advanced option has a value, validate the password
    if (passwordInput.value || aliasInput.value || maxClicksInput.value) {
        // If password validation fails, show advanced options and return false
        if (!validatePassword()) {
            // Show advanced options if they're hidden
            if (advancedOptions && !advancedOptions.classList.contains('show')) {
                advancedOptions.classList.add('show');
                advancedOptions.classList.remove('hidden');
                const advancedToggle = document.getElementById('advanced-options-toggle');
                if (advancedToggle) {
                    advancedToggle.classList.add('active');
                }
            }
            return false;
        }
    }
    
    // All validations passed
    return true;
}
