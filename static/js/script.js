// URL Shortener Generator Client-side JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize file input previews
    initFileInputPreview('logo');
    initFileInputPreview('favicon');
    
    // Initialize color picker
    initColorPicker();
    
    // Initialize deployment option handler
    initDeploymentOptions();
    
    // Form validation
    const form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        const nameInput = document.getElementById('name');
        if (!nameInput.value.trim()) {
            event.preventDefault();
            showError('Please enter a name for your URL shortener.');
            nameInput.focus();
        }
        
        // Add warning for Azure deployment
        const deploymentOption = document.querySelector('input[name="deployment_option"]:checked').value;
        if (deploymentOption === 'azure') {
            // Check if we should show the warning
            if (!localStorage.getItem('azure_warning_shown')) {
                const confirmMessage = 'You selected Azure deployment. This will open a browser window for authentication with Microsoft and deploy your URL shortener directly to Azure. Continue?';
                if (!confirm(confirmMessage)) {
                    event.preventDefault();
                    return;
                }
                // Remember that we've shown the warning
                localStorage.setItem('azure_warning_shown', 'true');
            }
            
            // Show a loading message
            const loadingMessage = document.createElement('div');
            loadingMessage.className = 'loading-message';
            loadingMessage.innerHTML = `
                <div class="loading-spinner"></div>
                <p>Deploying to Azure... This may take a few minutes. Please don't close this window.</p>
            `;
            document.querySelector('.container').appendChild(loadingMessage);
        }
    });
});

// Function to handle deployment options
function initDeploymentOptions() {
    const deploymentOptions = document.querySelectorAll('input[name="deployment_option"]');
    const footerText = document.querySelector('footer p');
    const originalFooterText = footerText.textContent;
    
    // Add help text for each option
    const deploymentHelpText = document.createElement('p');
    deploymentHelpText.className = 'help-text deployment-help-text';
    
    // Insert help text after the radio group
    const radioGroup = document.querySelector('.radio-group');
    radioGroup.parentNode.insertBefore(deploymentHelpText, radioGroup.nextSibling);
    
    // Function to update help text based on selected option
    function updateHelpText(value) {
        switch(value) {
            case 'docker':
                deploymentHelpText.textContent = 'Creates a Docker-ready package with docker-compose.yml for easy deployment';
                break;
            case 'standalone':
                deploymentHelpText.textContent = 'Creates a standalone Python application with detailed setup instructions';
                break;
            case 'azure':
                deploymentHelpText.textContent = 'Directly deploys to Azure App Service (free tier) and provides you a live URL';
                break;
        }
    }
    
    // Set initial help text
    updateHelpText(document.querySelector('input[name="deployment_option"]:checked').value);
    
    // Update help text when option changes
    deploymentOptions.forEach(option => {
        option.addEventListener('change', function() {
            updateHelpText(this.value);
        });
    });
}

// Function to initialize file input preview
function initFileInputPreview(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    // Create preview container if it doesn't exist
    let previewContainer = document.getElementById(`${inputId}-preview-container`);
    if (!previewContainer) {
        previewContainer = document.createElement('div');
        previewContainer.id = `${inputId}-preview-container`;
        previewContainer.className = 'preview-container';
        previewContainer.style.display = 'none';
        
        const previewImg = document.createElement('img');
        previewImg.id = `${inputId}-preview`;
        previewImg.className = 'preview-image';
        previewContainer.appendChild(previewImg);
        
        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'remove-preview';
        removeButton.innerHTML = '&times;';
        removeButton.addEventListener('click', function() {
            previewContainer.style.display = 'none';
            input.value = '';
        });
        previewContainer.appendChild(removeButton);
        
        // Insert the preview container after the input
        input.parentNode.insertBefore(previewContainer, input.nextSibling);
    }
    
    input.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            // Check file type
            const fileType = this.files[0].type;
            if (!fileType.startsWith('image/')) {
                showError(`Please select an image file for the ${inputId}.`);
                this.value = '';
                previewContainer.style.display = 'none';
                return;
            }
            
            // Check file size (max 2MB)
            if (this.files[0].size > 2 * 1024 * 1024) {
                showError(`The ${inputId} file is too large. Maximum size is 2MB.`);
                this.value = '';
                previewContainer.style.display = 'none';
                return;
            }
            
            // Create and show preview
            const reader = new FileReader();
            reader.onload = function(e) {
                const previewImg = document.getElementById(`${inputId}-preview`);
                previewImg.src = e.target.result;
                previewContainer.style.display = 'block';
            };
            reader.readAsDataURL(this.files[0]);
        } else {
            previewContainer.style.display = 'none';
        }
    });
}

// Function to initialize color picker
function initColorPicker() {
    const colorInput = document.getElementById('accent_color');
    const previewBox = document.querySelector('.preview-box');
    const previewButton = document.querySelector('.preview-button');
    const previewLink = document.querySelector('.preview-link');
    
    if (!colorInput) return;
    
    // Function to update colors
    function updateColors(color) {
        // Get a darker shade for hover effects
        const darkerColor = adjustColor(color, -15);
        
        // Update CSS variables
        document.documentElement.style.setProperty('--primary-color', color);
        document.documentElement.style.setProperty('--primary-dark', darkerColor);
        
        // Update preview elements
        if (previewBox) previewBox.style.backgroundColor = color;
        
        if (previewButton) {
            previewButton.style.backgroundColor = color;
            // Add hover effect
            previewButton.onmouseover = () => previewButton.style.backgroundColor = darkerColor;
            previewButton.onmouseout = () => previewButton.style.backgroundColor = color;
        }
        
        if (previewLink) {
            previewLink.style.color = color;
        }
        
        // Update generate button
        const generateBtn = document.querySelector('.generate-btn');
        if (generateBtn) {
            generateBtn.style.backgroundColor = color;
            generateBtn.onmouseover = () => generateBtn.style.backgroundColor = darkerColor;
            generateBtn.onmouseout = () => generateBtn.style.backgroundColor = color;
        }
    }
    
    // Initial color update
    updateColors(colorInput.value);
    
    // Listen for color changes
    colorInput.addEventListener('input', function() {
        updateColors(this.value);
    });
}

// Function to adjust color brightness
function adjustColor(color, amount) {
    const hex = color.replace('#', '');
    const r = Math.max(0, Math.min(255, parseInt(hex.substr(0, 2), 16) + amount));
    const g = Math.max(0, Math.min(255, parseInt(hex.substr(2, 2), 16) + amount));
    const b = Math.max(0, Math.min(255, parseInt(hex.substr(4, 2), 16) + amount));
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

// Function to show error message
function showError(message) {
    // Create flash message element
    const flashContainer = document.querySelector('.flash-messages');
    if (!flashContainer) {
        const container = document.createElement('div');
        container.className = 'flash-messages';
        document.querySelector('.container').insertBefore(container, document.querySelector('main'));
    }
    
    const flashMessage = document.createElement('div');
    flashMessage.className = 'flash-message';
    flashMessage.textContent = message;
    
    document.querySelector('.flash-messages').appendChild(flashMessage);
    
    // Remove the message after 5 seconds
    setTimeout(() => {
        flashMessage.remove();
        
        // If no more messages, remove the container
        const messagesContainer = document.querySelector('.flash-messages');
        if (messagesContainer && messagesContainer.children.length === 0) {
            messagesContainer.remove();
        }
    }, 5000);
} 