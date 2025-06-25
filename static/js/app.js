document.addEventListener('DOMContentLoaded', function() {
    // Initialize file upload handling
    const resumeForm = document.getElementById('resumeForm');
    const resumeFile = document.getElementById('resumeFile');
    const fileName = document.getElementById('fileName');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const alertContainer = document.getElementById('alertContainer');
    const resultsSection = document.getElementById('resultsSection');

    // Display selected filename
    if (resumeFile) {
        resumeFile.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileName.textContent = this.files[0].name;
                analyzeBtn.disabled = false;
            } else {
                fileName.textContent = 'No file selected';
                analyzeBtn.disabled = true;
            }
        });
    }

    // Handle form submission
    if (resumeForm) {
        resumeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!resumeFile.files.length) {
                showAlert('Please select a file to upload', 'danger');
                return;
            }
            
            const formData = new FormData();
            formData.append('resume', resumeFile.files[0]);
            
            // Show loading state
            setLoading(true);
            clearResults();
            
            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                setLoading(false);
                
                if (data.success) {
                    displayResults(data);
                } else {
                    showAlert(data.error || 'An error occurred while processing your resume', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                setLoading(false);
                showAlert('An error occurred while uploading your resume. Please try again.', 'danger');
            });
        });
    }

    // Helper functions
    function showAlert(message, type = 'danger') {
        alertContainer.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }

    function clearResults() {
        if (resultsSection) {
            resultsSection.classList.add('d-none');
        }
    }

    function setLoading(isLoading) {
        if (analyzeBtn && loadingSpinner) {
            if (isLoading) {
                analyzeBtn.disabled = true;
                loadingSpinner.classList.remove('d-none');
            } else {
                analyzeBtn.disabled = false;
                loadingSpinner.classList.add('d-none');
            }
        }
    }

    function displayResults(data) {
        if (!resultsSection) return;
        
        // Make results section visible
        resultsSection.classList.remove('d-none');
        
        // Display resume text
        const resumeText = document.getElementById('resumeText');
        if (resumeText) {
            resumeText.textContent = data.text;
        }
        
        // Display ATS score
        const scoreContainer = document.getElementById('scoreContainer');
        if (scoreContainer) {
            const scoreClass = getScoreColorClass(data.ats_score);
            const scoreMessage = getScoreMessage(data.ats_score);
            
            scoreContainer.innerHTML = `
                <div class="card-header">
                    <h5 class="card-title mb-0">ATS Compatibility Score</h5>
                </div>
                <div class="card-body text-center">
                    <div class="score-circle ${scoreClass}">
                        <span>${Math.round(data.ats_score)}</span>
                    </div>
                    <h5 class="mt-3">${data.top_job}</h5>
                    <p class="mt-2">${scoreMessage}</p>
                    <div class="mt-4">
                        <h6>Improvement Suggestions:</h6>
                        <ul class="text-start suggestion-list">
                            ${data.improvement_suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }
        
        // Display skills
        const skillsContainer = document.getElementById('skillsContainer');
        if (skillsContainer && data.skills) {
            skillsContainer.innerHTML = data.skills.length ? 
                data.skills.map(skill => `<span class="badge bg-primary me-2 mb-2 p-2">${skill}</span>`).join('') : 
                '<p class="text-muted">No skills detected. Consider adding more technical skills to your resume.</p>';
        }
        
        // Display sections
        const sectionsContainer = document.getElementById('sectionsContainer');
        if (sectionsContainer && data.sections) {
            let sectionsHtml = '<div class="accordion" id="sectionsAccordion">';
            
            let index = 0;
            for (const [section, content] of Object.entries(data.sections)) {
                if (content) {
                    sectionsHtml += `
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button ${index > 0 ? 'collapsed' : ''}" type="button" 
                                    data-bs-toggle="collapse" data-bs-target="#section${index}" 
                                    aria-expanded="${index === 0 ? 'true' : 'false'}" aria-controls="section${index}">
                                    ${section}
                                </button>
                            </h2>
                            <div id="section${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" 
                                data-bs-parent="#sectionsAccordion">
                                <div class="accordion-body">
                                    <pre class="mb-0">${content}</pre>
                                </div>
                            </div>
                        </div>
                    `;
                    index++;
                }
            }
            
            sectionsHtml += '</div>';
            
            if (index === 0) {
                sectionsHtml = '<p class="text-muted">No sections detected.</p>';
            }
            
            sectionsContainer.innerHTML = sectionsHtml;
        }
        
        // Display entities
        const entitiesContainer = document.getElementById('entitiesContainer');
        if (entitiesContainer && data.entities) {
            let entitiesHtml = '';
            
            for (const [entityType, entities] of Object.entries(data.entities)) {
                if (entities && entities.length) {
                    entitiesHtml += `
                        <div class="mb-4">
                            <h6>${entityType}</h6>
                            <div>
                                ${entities.map(entity => `<span class="badge bg-secondary me-2 mb-2 p-2">${entity}</span>`).join('')}
                            </div>
                        </div>
                    `;
                }
            }
            
            if (!entitiesHtml) {
                entitiesHtml = '<p class="text-muted">No entities detected.</p>';
            }
            
            entitiesContainer.innerHTML = entitiesHtml;
        }
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    function getScoreColorClass(score) {
        if (score >= 80) return 'score-high';
        if (score >= 60) return 'score-medium';
        return 'score-low';
    }

    function getScoreMessage(score) {
        if (score >= 80) {
            return 'Great! Your resume is well-optimized for ATS systems.';
        } else if (score >= 60) {
            return 'Your resume has a moderate chance of passing ATS systems. Consider implementing the suggestions to improve it.';
        } else {
            return 'Your resume may struggle to pass ATS systems. Follow the suggestions to significantly improve your chances.';
        }
    }

    // Add custom stylesheet for resume analyzer
    const style = document.createElement('style');
    style.textContent = `
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
            margin-bottom: 15px;
            transition: all 0.3s;
        }
        .upload-area:hover {
            border-color: var(--bs-primary);
        }
        .file-name {
            margin-top: 10px;
            font-weight: 500;
        }
        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            font-size: 36px;
            font-weight: bold;
            color: white;
        }
        .score-high {
            background-color: #198754;
        }
        .score-medium {
            background-color: #fd7e14;
        }
        .score-low {
            background-color: #dc3545;
        }
        .suggestion-list li {
            margin-bottom: 8px;
        }
        pre {
            white-space: pre-wrap;
            background-color: rgba(0,0,0,0.05);
            padding: 10px;
            border-radius: 4px;
        }
        .hero-section {
            padding: 3rem 0;
            background-color: var(--bs-dark);
            margin-bottom: 2rem;
        }
        .hero-title {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: white;
        }
        .hero-subtitle {
            font-size: 1.2rem;
            opacity: 0.8;
            color: white;
        }
    `;
    document.head.appendChild(style);
});