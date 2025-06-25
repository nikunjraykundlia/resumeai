// Charts JavaScript for Resume Analyzer application

// Initialize ATS Score Chart when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeAtsScoreChart();
});

// Initialize ATS Score Donut Chart
function initializeAtsScoreChart() {
    const atsScoreElement = document.getElementById('ats-score-chart');
    if (!atsScoreElement) return;
    
    const scoreValue = parseInt(atsScoreElement.dataset.score || 0);
    
    const ctx = atsScoreElement.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [scoreValue, 100 - scoreValue],
                backgroundColor: getAtsScoreColors(scoreValue),
                borderWidth: 0
            }]
        },
        options: {
            cutout: '80%',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        }
    });
}

// Get color scheme based on ATS score
function getAtsScoreColors(score) {
    if (score >= 80) {
        // Excellent - Green
        return ['rgba(40, 167, 69, 0.8)', 'rgba(211, 211, 211, 0.3)'];
    } else if (score >= 60) {
        // Good - Blue
        return ['rgba(0, 123, 255, 0.8)', 'rgba(211, 211, 211, 0.3)'];
    } else if (score >= 40) {
        // Average - Yellow
        return ['rgba(255, 193, 7, 0.8)', 'rgba(211, 211, 211, 0.3)'];
    } else {
        // Needs Improvement - Red
        return ['rgba(220, 53, 69, 0.8)', 'rgba(211, 211, 211, 0.3)'];
    }
}

// Initialize skill distribution chart
function initializeSkillDistributionChart() {
    const skillChartElement = document.getElementById('skill-distribution-chart');
    if (!skillChartElement) return;
    
    // Parse data from the data attributes
    const skillsData = JSON.parse(skillChartElement.dataset.skills || '{}');
    const labels = Object.keys(skillsData);
    const data = Object.values(skillsData);
    
    const ctx = skillChartElement.getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Skill Proficiency',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
            }]
        },
        options: {
            elements: {
                line: {
                    borderWidth: 3
                }
            },
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            }
        }
    });
}

// Initialize job match chart
function initializeJobMatchChart() {
    const jobMatchChartElement = document.getElementById('job-match-chart');
    if (!jobMatchChartElement) return;
    
    // Parse data from the data attributes
    const jobsData = JSON.parse(jobMatchChartElement.dataset.jobs || '[]');
    const labels = jobsData.map(job => job.title);
    const data = jobsData.map(job => job.match);
    
    const ctx = jobMatchChartElement.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Match %',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.8)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            scales: {
                x: {
                    beginAtZero: true,
                    suggestedMax: 100
                }
            }
        }
    });
}
