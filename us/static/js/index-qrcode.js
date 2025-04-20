// Get all elements with the "stats-button" class
const statsButtons = document.querySelectorAll('.stats-button');

// Add click event listener to each stats button
statsButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Get the short code from the URL in the card
        const shortUrlElement = button.closest('.url-container').querySelector('.short-url a');
        const href = shortUrlElement.getAttribute('href');
        const shortCode = href.substring(1); // Remove the leading slash
        
        // Navigate to the stats page using the 'short' query parameter
        // The backend will redirect to /stats/{shortCode}
        window.location.href = `/stats?short=${encodeURIComponent(shortCode)}`;
    });
});


const copyButtons = document.querySelectorAll('.copy-button');
// Add click event listener to each copy button
copyButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Get the URL from the data-url attribute of the button
        const url = button.getAttribute('data-url');

        // Use modern clipboard API if available
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(url)
                .then(() => {
                    // Provide visual feedback to indicate successful copying
                    const originalText = button.innerHTML;
                    button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="button-icon"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied!';
                    setTimeout(() => {
                        button.innerHTML = originalText;
                    }, 1500);
                })
                .catch(err => {
                    console.error('Failed to copy text: ', err);
                    fallbackCopyText(url, button);
                });
        } else {
            fallbackCopyText(url, button);
        }
    });
});

// Fallback copy method
function fallbackCopyText(text, button) {
    // Create a temporary input element to copy the URL
    const tempInput = document.createElement('input');
    tempInput.value = text;
    document.body.appendChild(tempInput);

    // Select the URL in the input element
    tempInput.select();
    tempInput.setSelectionRange(0, 99999); // For mobile devices

    // Copy the URL to the clipboard
    document.execCommand('copy');

    // Remove the temporary input element
    document.body.removeChild(tempInput);

    // Provide visual feedback
    const originalText = button.innerHTML;
    button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="button-icon"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied!';
    setTimeout(() => {
        button.innerHTML = originalText;
    }, 1500);
}

// Get all elements with the "qr-code" class
const qrCodeElements = document.querySelectorAll('.qr-code');

// Iterate over each QR code element
qrCodeElements.forEach(element => {
    // Get the URL from the data-url attribute
    const url = element.getAttribute('data-url');

    // Generate the QR code using QRCode.js
    const qrcode = new QRCode(element, {
        text: url,
        width: 65,
        height: 65,
        correctLevel: QRCode.CorrectLevel.L,
        margin: 0,
        colorDark: '#000000',
        colorLight: '#ffffff',
    });
});




// QR Code Popup functionality
const qrPopup = document.getElementById('qr-popup');
const closePopup = document.querySelector('.close-popup');
const popupQrCode = document.getElementById('popup-qr-code');
const popupUrl = document.getElementById('popup-url');
const downloadQrButton = document.getElementById('download-qr');

// Function to show QR code popup
function showQRCodePopup(url) {
    // Clear previous QR code
    popupQrCode.innerHTML = '';
    
    // Generate new QR code
    const qrcode = new QRCode(popupQrCode, {
        text: url,
        width: 300,
        height: 300,
        correctLevel: QRCode.CorrectLevel.H,
        colorDark: '#000000',
        colorLight: '#ffffff',
    });
    
    // Set URL text
    popupUrl.textContent = url;
    
    // Show popup
    qrPopup.style.display = 'block';
    
    // Set up download button
    downloadQrButton.onclick = function() {
        // Get the QR code image
        const img = popupQrCode.querySelector('img');
        
        // Create a link to download the image
        const link = document.createElement('a');
        link.href = img.src;
        link.download = 'qrcode.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
}

// Close popup when clicking the X button
closePopup.addEventListener('click', function() {
    qrPopup.style.display = 'none';
});

// Close popup when clicking outside the content
window.addEventListener('click', function(event) {
    if (event.target === qrPopup) {
        qrPopup.style.display = 'none';
    }
});

// Add missing String.prototype.includes polyfill for older browsers
if (!String.prototype.includes) {
    String.prototype.includes = function(search, start) {
        'use strict';
        if (typeof start !== 'number') {
            start = 0;
        }
        
        if (start + search.length > this.length) {
            return false;
        } else {
            return this.indexOf(search, start) !== -1;
        }
    };
}

// Add Element.prototype.querySelector polyfill for older browsers
if (!Element.prototype.querySelector) {
    Element.prototype.querySelector = function(selectors) {
        return this.getElementsByTagName(selectors)[0] || null;
    };
}