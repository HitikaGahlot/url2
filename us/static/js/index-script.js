function toggleDropdown() {
    const dropdown = document.querySelector('.dropdown');
    dropdown.classList.toggle('dropdown-expanded');
}

const inputBox = document.querySelector('#alias');

inputBox.addEventListener('focus', (e) => {
    document.querySelector('.buttonIn').classList.add('focus');
});

inputBox.addEventListener('blur', (e) => {
    document.querySelector('.buttonIn').classList.remove('focus');
});

function get_metrics() {
    fetch('/metric')
        .then(response => response.json())
        .then(data => {
            document.querySelector('#total-urls').textContent = data["total-shortlinks"];
            document.querySelector('#total-clicks').textContent = data["total-clicks"];
        });

    fetch('https://discord.com/api/guilds/1192388005206433892/widget.json')
        .then(response => response.json())
        .then(data => {
            document.querySelector('#discord-online').textContent = data["presence_count"]+"+";
        });

    fetch('https://api.github.com/repos/yourorganization/url-shortener')
        .then(response => response.json())
        .then(data => {
            document.querySelector('#github-stars').textContent = data["stargazers_count"];
        });
}

document.onload = get_metrics();

document.addEventListener("DOMContentLoaded", function() {
    // Setup advanced options toggle
    const advancedToggle = document.getElementById('advanced-options-toggle');
    const advancedOptions = document.getElementById('advanced-options');

    if (advancedToggle && advancedOptions) {
        advancedToggle.addEventListener('click', function() {
            advancedToggle.classList.toggle('active');
            advancedOptions.classList.toggle('show');
            advancedOptions.classList.toggle('hidden');
        });
    }

    // Handle copy buttons
    document.querySelectorAll('.copy-button').forEach(button => {
        button.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            navigator.clipboard.writeText(url).then(() => {
                // Show success notification
                customTopNotification('success', 'URL copied to clipboard!', 3);
            }).catch(err => {
                console.error('Could not copy text: ', err);
            });
        });
    });

    // Handle stats buttons
    document.querySelectorAll('.stats-button').forEach(button => {
        button.addEventListener('click', function() {
            const urlContainer = this.closest('.url-container');
            const shortUrl = urlContainer.querySelector('.short-url a').textContent;
            const urlCode = shortUrl.split('/').pop();
            window.location.href = `/stats?short=${urlCode}`;
        });
    });

    // Error handling
    const urlError = document.getElementById('url-error');
    const passwordError = document.getElementById('password-error');

    // Only show error elements when they have content
    if (urlError) {
        urlError.classList.add('hidden');
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.target.textContent.trim()) {
                    mutation.target.classList.remove('hidden');
                } else {
                    mutation.target.classList.add('hidden');
                }
            });
        });
        
        observer.observe(urlError, { childList: true, characterData: true, subtree: true });
    }

    if (passwordError) {
        passwordError.classList.add('hidden');
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.target.textContent.trim()) {
                    mutation.target.classList.remove('hidden');
                } else {
                    mutation.target.classList.add('hidden');
                }
            });
        });
        
        observer.observe(passwordError, { childList: true, characterData: true, subtree: true });
    }
});