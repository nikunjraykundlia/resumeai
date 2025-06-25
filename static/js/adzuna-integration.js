/**
 * Adzuna Integration Script
 * This script is injected into Adzuna's search page to assist with form filling
 */

(function() {
    console.log('Adzuna Integration Script loaded');
    
    // Helper function to get parameters from URL
    function getParameterByName(name, url = window.location.href) {
        name = name.replace(/[\[\]]/g, '\\$&');
        const regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, ' '));
    }
    
    // Try to get values from URL parameters first (most reliable)
    let jobTitle = getParameterByName('q');
    let jobLocation = getParameterByName('w');
    
    // If not in URL, try localStorage or cookies
    if (!jobTitle) {
        jobTitle = localStorage.getItem('adzuna_job_title');
        if (!jobTitle) {
            // Try to get from cookie
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith('adzuna_job_title=')) {
                    jobTitle = decodeURIComponent(cookie.substring('adzuna_job_title='.length));
                    break;
                }
            }
        }
    }
    
    if (!jobLocation) {
        jobLocation = localStorage.getItem('adzuna_job_location');
        if (!jobLocation) {
            // Try to get from cookie
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith('adzuna_job_location=')) {
                    jobLocation = decodeURIComponent(cookie.substring('adzuna_job_location='.length));
                    break;
                }
            }
        }
    }
    
    // If we have values, fill the form
    if (jobTitle || jobLocation) {
        console.log('Found search parameters:', { jobTitle, jobLocation });
        
        // Function to fill form fields
        function fillFormFields() {
            // Direct approach for Adzuna's green search bar
            const whatInput = document.querySelector('.what-search, input[placeholder*="job"], input[placeholder*="What"], input[name="what"], input#what');
            const whereInput = document.querySelector('.where-search, input[placeholder*="location"], input[placeholder*="Where"], input[name="where"], input#where');
            
            let filled = false;
            
            if (whatInput && jobTitle) {
                whatInput.value = jobTitle;
                whatInput.dispatchEvent(new Event('input', { bubbles: true }));
                console.log('Filled job title field');
                filled = true;
            }
            
            if (whereInput && jobLocation) {
                whereInput.value = jobLocation;
                whereInput.dispatchEvent(new Event('input', { bubbles: true }));
                console.log('Filled location field');
                filled = true;
            }
            
            // If exact selectors didn't work, try more generic approach
            if (!filled) {
                const inputs = document.querySelectorAll('input[type="text"], input:not([type])');
                
                if (inputs.length >= 2) {
                    // Assume first input is job title, second is location (common pattern)
                    if (jobTitle) {
                        inputs[0].value = jobTitle;
                        inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                    }
                    
                    if (jobLocation) {
                        inputs[1].value = jobLocation;
                        inputs[1].dispatchEvent(new Event('input', { bubbles: true }));
                    }
                    
                    console.log('Filled form fields with generic approach');
                }
            }
            
            // Clean up after filling
            localStorage.removeItem('adzuna_job_title');
            localStorage.removeItem('adzuna_job_location');
        }
        
        // Try immediately
        fillFormFields();
        
        // Also try after a delay to handle dynamic content loading
        setTimeout(fillFormFields, 500);
        setTimeout(fillFormFields, 1000);
        setTimeout(fillFormFields, 2000);
    }
})();