// Skills Test JavaScript for Resume Analyzer application

// Global variables
let skillQuestions = [];
let currentQuestionIndex = 0;
let userAnswers = {};
let skillResults = {};

function initializeSkillTest() {
    const skillTestContainer = document.getElementById('skill-test-container');
    const skills = Array.from(document.querySelectorAll('.skill-badge')).map(badge => badge.textContent.trim());
    
    if (!skillTestContainer || !skills.length) return;
    
    // Generate questions based on the skills
    generateSkillQuestions(skills);
}

function generateSkillQuestions(skills) {
    // Show loading state
    const testContainer = document.getElementById('skill-test-container');
    testContainer.innerHTML = `
        <div class="text-center p-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">Generating skill assessment questions...</p>
            <p class="text-muted small">Crafting challenging questions tailored to your skills</p>
        </div>
    `;
    
    // Initialize skills with zero scores
    skills.forEach(skill => {
        skillResults[skill] = 0;
    });

    // Fetch questions from our API
    fetch('/api/get_skill_questions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ skills: skills })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.questions && data.questions.length > 0) {
            // Got questions from the API
            skillQuestions = data.questions;
            showQuestion();
        } else {
            // API failed, fallback to local questions
            console.warn("API didn't return valid questions, using fallback");
            fallbackGenerateQuestions(skills);
        }
    })
    .catch(error => {
        console.error('Error fetching skill questions:', error);
        fallbackGenerateQuestions(skills);
    });
}

function fallbackGenerateQuestions(skills) {
    // Fallback question templates if API call fails
    const questionTemplate = {
        Python: [
            {
                question: "What is the output of the following Python code?\n\nx = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)",
                options: ['[1, 2, 3]', '[1, 2, 3, 4]', '[4, 1, 2, 3]', 'Error'],
                answer: '[1, 2, 3, 4]'
            },
            {
                question: "Which of the following is NOT a built-in data type in Python?",
                options: ['List', 'Dictionary', 'Array', 'Tuple'],
                answer: 'Array'
            }
        ],
        JavaScript: [
            {
                question: "What is the output of console.log(1 + '2' + '2');",
                options: ['122', '32', '14', 'Error'],
                answer: '122'
            },
            {
                question: "Which of the following is NOT a JavaScript framework or library?",
                options: ['React', 'Vue', 'Django', 'Angular'],
                answer: 'Django'
            }
        ],
        Java: [
            {
                question: "What is the parent class of all classes in Java?",
                options: ['String', 'System', 'Object', 'Root'],
                answer: 'Object'
            },
            {
                question: "Which of the following is not a valid access modifier in Java?",
                options: ['public', 'private', 'protected', 'friend'],
                answer: 'friend'
            }
        ],
        HTML: [
            {
                question: "Which HTML tag is used to define an internal style sheet?",
                options: ['<script>', '<style>', '<html>', '<css>'],
                answer: '<style>'
            },
            {
                question: "Which HTML attribute is used to define inline styles?",
                options: ['styles', 'style', 'class', 'font'],
                answer: 'style'
            },
            {
                question: "What is the correct HTML element for the largest heading?",
                options: ['<heading>', '<h1>', '<h6>', '<head>'],
                answer: '<h1>'
            },
            {
                question: "Which HTML tag is used to create a hyperlink?",
                options: ['<link>', '<a>', '<hlink>', '<url>'],
                answer: '<a>'
            }
        ],
        CSS: [
            {
                question: "Which CSS property controls the text size?",
                options: ['text-size', 'font-size', 'text-style', 'font-style'],
                answer: 'font-size'
            },
            {
                question: "What does CSS stand for?",
                options: ['Cascading Style Sheets', 'Computer Style Sheets', 'Creative Style Sheets', 'Colorful Style Sheets'],
                answer: 'Cascading Style Sheets'
            }
        ],
        SQL: [
            {
                question: "Which SQL statement is used to extract data from a database?",
                options: ['GET', 'EXTRACT', 'SELECT', 'OPEN'],
                answer: 'SELECT'
            },
            {
                question: "Which SQL keyword is used to filter results?",
                options: ['FILTER', 'WHERE', 'LIMIT', 'HAVING'],
                answer: 'WHERE'
            }
        ],
        "React.js": [
            {
                question: "What function is used to update state in a React class component?",
                options: ['this.state()', 'this.setState()', 'this.updateState()', 'this.changeState()'],
                answer: 'this.setState()'
            },
            {
                question: "In React, what is used to pass data to a component from outside?",
                options: ['setState', 'props', 'render', 'PropTypes'],
                answer: 'props'
            }
        ]
    };
    
    // Add generic questions for any skills not covered
    const genericQuestions = [
        {
            skill: "Problem Solving",
            question: "What approach would you take to solve a complex programming problem?",
            options: [
                'Break it down into smaller components and solve each one',
                'Look for existing solutions online and adapt them',
                'Ask a colleague for help immediately',
                'Try solving the entire problem at once'
            ],
            answer: 'Break it down into smaller components and solve each one'
        },
        {
            skill: "Software Development",
            question: "Which development methodology emphasizes adaptive planning and continuous improvement?",
            options: ['Waterfall', 'Agile', 'Big Bang', 'Critical Path Method'],
            answer: 'Agile'
        },
        {
            skill: "Version Control",
            question: "What is the purpose of branching in Git?",
            options: [
                'To duplicate the repository',
                'To work on features or fixes without affecting the main codebase',
                'To permanently split a project into two versions',
                'To backup the code'
            ],
            answer: 'To work on features or fixes without affecting the main codebase'
        }
    ];
    
    // Generate questions for the skills
    skillQuestions = [];
    for (const skill of skills) {
        // Find the skill in the template (case-insensitive)
        const skillKey = Object.keys(questionTemplate).find(
            k => k.toLowerCase() === skill.toLowerCase()
        );
        
        if (skillKey && questionTemplate[skillKey].length > 0) {
            // Add a random question for this skill
            const randomIndex = Math.floor(Math.random() * questionTemplate[skillKey].length);
            skillQuestions.push({
                skill: skill,
                ...questionTemplate[skillKey][randomIndex]
            });
        }
    }
    
    // If we have fewer than 3 questions, add some generic ones
    while (skillQuestions.length < 3 && genericQuestions.length > 0) {
        const genericQuestion = genericQuestions.shift();
        skillQuestions.push(genericQuestion);
    }
    
    // Limit to 5 questions maximum
    skillQuestions = skillQuestions.slice(0, 5);
    
    // Start the test
    showQuestion();
}

function showQuestion() {
    const testContainer = document.getElementById('skill-test-container');
    const progressElement = document.getElementById('test-progress');
    
    if (currentQuestionIndex < skillQuestions.length) {
        const question = skillQuestions[currentQuestionIndex];
        
        // Update progress indicator
        if (progressElement) {
            progressElement.textContent = `Question ${currentQuestionIndex + 1} of ${skillQuestions.length}`;
        }
        
        // Create the question HTML
        let questionHTML = `
            <div class="skill-question card mb-4">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">${question.skill}</h5>
                </div>
                <div class="card-body">
                    <p class="card-text">${question.question}</p>
                    <div class="skill-answers">
        `;
        
        // Add options
        question.options.forEach((option, index) => {
            questionHTML += `
                <div class="form-check skill-answer">
                    <input class="form-check-input" type="radio" name="q${currentQuestionIndex}" 
                           id="q${currentQuestionIndex}o${index}" value="${option}">
                    <label class="form-check-label" for="q${currentQuestionIndex}o${index}">
                        ${option}
                    </label>
                </div>
            `;
        });
        
        // Add navigation buttons
        questionHTML += `
                    </div>
                </div>
                <div class="card-footer d-flex justify-content-between">
                    <button class="btn btn-outline-secondary" onclick="previousQuestion()" 
                        ${currentQuestionIndex === 0 ? 'disabled' : ''}>
                        Previous
                    </button>
                    <button class="btn btn-primary" onclick="nextQuestion()">
                        ${currentQuestionIndex === skillQuestions.length - 1 ? 'Finish' : 'Next'}
                    </button>
                </div>
            </div>
        `;
        
        testContainer.innerHTML = questionHTML;
        
        // Restore previous answer if available
        if (userAnswers[currentQuestionIndex] !== undefined) {
            const selectedOption = userAnswers[currentQuestionIndex];
            const radioButton = document.querySelector(`input[name="q${currentQuestionIndex}"][value="${selectedOption}"]`);
            if (radioButton) {
                radioButton.checked = true;
            }
        }
    } else {
        // Test is complete, calculate results
        calculateResults();
    }
}

function previousQuestion() {
    if (currentQuestionIndex > 0) {
        saveCurrentAnswer();
        currentQuestionIndex--;
        showQuestion();
    }
}

function nextQuestion() {
    saveCurrentAnswer();
    
    if (currentQuestionIndex < skillQuestions.length - 1) {
        currentQuestionIndex++;
        showQuestion();
    } else {
        // This is the last question, finish the test
        calculateResults();
    }
}

function saveCurrentAnswer() {
    const selectedOption = document.querySelector(`input[name="q${currentQuestionIndex}"]:checked`);
    if (selectedOption) {
        userAnswers[currentQuestionIndex] = selectedOption.value;
    }
}

function calculateResults() {
    // Calculate score for each skill
    skillQuestions.forEach((question, index) => {
        const userAnswer = userAnswers[index];
        const correctAnswer = question.answer;
        const isCorrect = userAnswer === correctAnswer;
        
        if (isCorrect) {
            // If the skill isn't in our results yet, initialize it
            if (skillResults[question.skill] === undefined) {
                skillResults[question.skill] = 0;
            }
            // Increase skill score
            skillResults[question.skill] += 100;
        }
    });
    
    // Average the scores for skills with multiple questions
    const questionCountBySkill = {};
    skillQuestions.forEach(question => {
        if (questionCountBySkill[question.skill] === undefined) {
            questionCountBySkill[question.skill] = 0;
        }
        questionCountBySkill[question.skill]++;
    });
    
    Object.keys(skillResults).forEach(skill => {
        if (questionCountBySkill[skill]) {
            skillResults[skill] = Math.round(skillResults[skill] / questionCountBySkill[skill]);
        }
    });
    
    // Show results
    showResults();
}

function showResults() {
    const testContainer = document.getElementById('skill-test-container');
    const resultHTML = `
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0">Skills Assessment Complete</h5>
            </div>
            <div class="card-body">
                <h6 class="card-subtitle mb-3 text-muted">Your skill proficiency levels:</h6>
                <div class="row" id="skill-charts-container">
                    ${Object.keys(skillResults).map(skill => `
                        <div class="col-md-4 mb-3">
                            <div class="card h-100">
                                <div class="card-body text-center">
                                    <h6>${skill}</h6>
                                    <div class="skill-chart" data-skill="${skill}" data-score="${skillResults[skill]}">
                                        <canvas id="chart-${skill.replace(/\s+/g, '-').toLowerCase()}"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="card-footer text-center">
                <button class="btn btn-primary" onclick="submitSkillResults()">
                    Continue to Job Recommendations
                </button>
            </div>
        </div>
    `;
    
    testContainer.innerHTML = resultHTML;
    
    // Initialize charts for each skill
    Object.keys(skillResults).forEach(skill => {
        const canvasId = `chart-${skill.replace(/\s+/g, '-').toLowerCase()}`;
        const canvas = document.getElementById(canvasId);
        
        if (canvas) {
            const ctx = canvas.getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [skillResults[skill], 100 - skillResults[skill]],
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(211, 211, 211, 0.3)'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    cutout: '70%',
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
            
            // Add percentage in the center
            const centerText = document.createElement('div');
            centerText.style.position = 'absolute';
            centerText.style.top = '50%';
            centerText.style.left = '50%';
            centerText.style.transform = 'translate(-50%, -50%)';
            centerText.style.textAlign = 'center';
            centerText.innerHTML = `<span style="font-size: 1.5rem; font-weight: bold;">${skillResults[skill]}%</span>`;
            
            const chartContainer = canvas.parentElement;
            chartContainer.style.position = 'relative';
            chartContainer.appendChild(centerText);
        }
    });
}

function submitSkillResults() {
    // Send the results to the server
    fetch('/submit_skill_test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            skill_results: skillResults
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.redirect) {
            window.location.href = data.redirect;
        } else {
            console.error('Error submitting results:', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
