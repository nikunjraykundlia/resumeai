// Main JavaScript for Resume Analyzer application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize drag and drop file upload
    initializeFileUpload();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize progress steps
    updateProgressIndicator();
    
    // Handle skill test if on skills test page
    if (document.getElementById('skill-test-container')) {
        initializeSkillTest();
    }
    
    // Handle resume preview if on analysis page
    if (document.getElementById('resume-preview')) {
        loadResumePreview();
    }
    
    // Check if we're on adzuna.com and auto-fill the search form
    if (window.location.hostname.includes('adzuna')) {
        autofillAdzunaForm();
    }
});

// File upload functionality
function initializeFileUpload() {
    const fileInput = document.getElementById('resume-file');
    const uploadForm = document.getElementById('upload-form');
    const dropArea = document.querySelector('.resume-uploader');
    const fileNameDisplay = document.getElementById('file-name');
    
    if (!fileInput || !dropArea) return;
    
    // Handle file selection
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            fileNameDisplay.textContent = fileInput.files[0].name;
            dropArea.classList.add('border-primary');
            
            // Enable the submit button
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = false;
        } else {
            fileNameDisplay.textContent = 'No file selected';
            dropArea.classList.remove('border-primary');
        }
    });
    
    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, function() {
            dropArea.classList.add('drag-over');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, function() {
            dropArea.classList.remove('drag-over');
        }, false);
    });
    
    dropArea.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            fileNameDisplay.textContent = files[0].name;
            dropArea.classList.add('border-primary');
            
            // Enable the submit button
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = false;
        }
    }, false);
    
    // Form submission - show loading state
    if (uploadForm) {
        uploadForm.addEventListener('submit', function() {
            document.getElementById('upload-content').classList.add('d-none');
            document.getElementById('loading-content').classList.remove('d-none');
        });
    }
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Update progress indicator based on current page
function updateProgressIndicator() {
    const progressIndicator = document.querySelector('.progress-indicator');
    if (!progressIndicator) return;
    
    const currentPage = document.body.dataset.page;
    const steps = progressIndicator.querySelectorAll('.progress-step');
    
    let activeFound = false;
    
    steps.forEach(step => {
        const stepId = step.dataset.step;
        const circle = step.querySelector('.step-circle');
        
        if (stepId === currentPage) {
            circle.classList.add('active');
            activeFound = true;
        } else if (!activeFound) {
            circle.classList.add('completed');
        }
    });
}

// Load resume preview text
function loadResumePreview() {
    const previewContainer = document.getElementById('resume-preview');
    if (!previewContainer) return;
    
    fetch('/api/resume_text')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                previewContainer.textContent = data.resume_text;
            } else {
                previewContainer.textContent = 'Failed to load resume text.';
            }
        })
        .catch(error => {
            console.error('Error fetching resume text:', error);
            previewContainer.textContent = 'Error loading resume text.';
        });
}

// Copy text to clipboard
function copyToClipboard(text, buttonElement) {
    navigator.clipboard.writeText(text).then(function() {
        // Change button text temporarily
        const originalText = buttonElement.textContent;
        buttonElement.textContent = 'Copied!';
        setTimeout(() => {
            buttonElement.textContent = originalText;
        }, 2000);
    }).catch(function(err) {
        console.error('Failed to copy text: ', err);
    });
}

// Toggle visibility of a section
function toggleSection(sectionId, buttonElement) {
    const section = document.getElementById(sectionId);
    if (section.classList.contains('d-none')) {
        section.classList.remove('d-none');
        buttonElement.innerHTML = 'Hide <i class="bi bi-chevron-up"></i>';
    } else {
        section.classList.add('d-none');
        buttonElement.innerHTML = 'Show <i class="bi bi-chevron-down"></i>';
    }
}

// Helper function to get cookie value by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
    return null;
}

// Function to auto-fill Adzuna search form
function autofillAdzunaForm() {
    try {
        // Try to get the stored values from either localStorage or cookies
        let jobTitle = localStorage.getItem('adzuna_job_title');
        let jobLocation = localStorage.getItem('adzuna_job_location');
        
        // If not in localStorage, try cookies (might work better across domains)
        if (!jobTitle) jobTitle = getCookie('adzuna_job_title');
        if (!jobLocation) jobLocation = getCookie('adzuna_job_location');
        
        // Also check URL parameters which is the most reliable method
        const urlParams = new URLSearchParams(window.location.search);
        const titleFromUrl = urlParams.get('q');
        const locationFromUrl = urlParams.get('w');
        
        // Prioritize URL parameters if they exist
        if (titleFromUrl) jobTitle = titleFromUrl;
        if (locationFromUrl) jobLocation = locationFromUrl;
        
        // If we have values, try to find and fill the search fields
        if (jobTitle || jobLocation) {
            console.log('Attempting to fill Adzuna search form with:', { jobTitle, jobLocation });
            
            // We'll try multiple times with increasing delays to ensure we can fill the form
            // even if it loads dynamically or has delays
            const attemptFill = (attempt = 1) => {
                // Try to find the search fields by direct targeting of Adzuna's green search bar
                console.log(`Attempt ${attempt} to fill Adzuna search form`);
                
                // Direct targeting based on the specific Adzuna search bar shown in your screenshot
                const searchForm = document.querySelector('.search-form, form');
                const whatField = document.querySelector('input[placeholder*="job"], input[placeholder*="title"], input[placeholder*="company"], input[placeholder*="What"]');
                const whereField = document.querySelector('input[placeholder*="city"], input[placeholder*="state"], input[placeholder*="ZIP"], input[placeholder*="Where"]');
                
                let filled = false;
                
                // If we found direct matches, use them
                if (whatField && jobTitle) {
                    whatField.value = jobTitle;
                    whatField.dispatchEvent(new Event('input', { bubbles: true }));
                    whatField.dispatchEvent(new Event('change', { bubbles: true }));
                    console.log('Filled "What?" field with', jobTitle);
                    filled = true;
                }
                
                if (whereField && jobLocation) {
                    whereField.value = jobLocation;
                    whereField.dispatchEvent(new Event('input', { bubbles: true }));
                    whereField.dispatchEvent(new Event('change', { bubbles: true }));
                    console.log('Filled "Where?" field with', jobLocation);
                    filled = true;
                }
                
                // If direct targeting failed, try a more generic approach
                if (!filled) {
                    console.log('Direct targeting failed, trying generic approach');
                    // Try to find all text inputs
                    const allInputs = document.querySelectorAll('input[type="text"], input:not([type])');
                    
                    if (allInputs.length >= 2) {
                        // Assume first field is what, second is where (common pattern)
                        if (jobTitle) {
                            allInputs[0].value = jobTitle;
                            allInputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                            allInputs[0].dispatchEvent(new Event('change', { bubbles: true }));
                            console.log('Filled first input with job title');
                        }
                        
                        if (jobLocation) {
                            allInputs[1].value = jobLocation;
                            allInputs[1].dispatchEvent(new Event('input', { bubbles: true }));
                            allInputs[1].dispatchEvent(new Event('change', { bubbles: true }));
                            console.log('Filled second input with location');
                        }
                        
                        filled = true;
                    }
                }
                
                // We'll try directly targeting the specific Adzuna search form elements
                // based on the exact structure seen in your screenshot
                if (!filled) {
                    console.log('Attempting to target specific Adzuna search elements');
                    
                    // Try using document.evaluate for XPath to get very specific nodes
                    try {
                        // First input in the green bar
                        const whatXPath = "//div[contains(@class,'search-bar')]//input[1]";
                        const whereXPath = "//div[contains(@class,'search-bar')]//input[2]";
                        
                        const whatResult = document.evaluate(whatXPath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                        const whereResult = document.evaluate(whereXPath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                        
                        const whatNode = whatResult.singleNodeValue;
                        const whereNode = whereResult.singleNodeValue;
                        
                        if (whatNode && jobTitle) {
                            whatNode.value = jobTitle;
                            whatNode.dispatchEvent(new Event('input', { bubbles: true }));
                            whatNode.dispatchEvent(new Event('change', { bubbles: true }));
                            console.log('Filled what field via XPath');
                            filled = true;
                        }
                        
                        if (whereNode && jobLocation) {
                            whereNode.value = jobLocation;
                            whereNode.dispatchEvent(new Event('input', { bubbles: true }));
                            whereNode.dispatchEvent(new Event('change', { bubbles: true }));
                            console.log('Filled where field via XPath');
                            filled = true;
                        }
                    } catch (e) {
                        console.log('XPath approach failed:', e);
                    }
                }
                
                // If we haven't filled the fields and we haven't tried too many times, try again after a delay
                if (!filled && attempt < 5) {
                    console.log(`Fill attempt ${attempt} failed, trying again in ${attempt * 500}ms`);
                    setTimeout(() => attemptFill(attempt + 1), attempt * 500);
                } else if (filled) {
                    console.log('Successfully filled Adzuna search form');
                    // Optional: Submit the form
                    // if (searchForm) searchForm.submit();
                    
                    // Clean up localStorage
                    localStorage.removeItem('adzuna_job_title');
                    localStorage.removeItem('adzuna_job_location');
                } else {
                    console.warn('Failed to fill Adzuna search form after multiple attempts');
                }
            };
            
            // Start the first attempt after a short delay
            setTimeout(() => attemptFill(), 500);
        }
    } catch (err) {
        console.error('Error auto-filling Adzuna search form:', err);
    }
}
