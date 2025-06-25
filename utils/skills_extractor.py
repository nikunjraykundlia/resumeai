import spacy
import pandas as pd
import re
import logging
import json
import os

# Import OpenAI helper
try:
    from openai import OpenAI
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    openai = OpenAI(api_key=OPENAI_API_KEY)
    OPENAI_AVAILABLE = True and OPENAI_API_KEY is not None
    # Constants for model selection
    GPT_MODEL = "gpt-4o"  # Using GPT-4o which is the latest model
except Exception as e:
    logging.error(f"Error initializing OpenAI for skills extraction: {str(e)}")
    OPENAI_AVAILABLE = False

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except Exception as e:
    logging.error(f"Error loading spaCy model: {str(e)}")
    nlp = None

# Load skills list
try:
    skills_dataset_path = 'attached_assets/expanded_skills_with_web_app_and_database.csv'
    skills_df = pd.read_csv(skills_dataset_path)
    skills_list = [skill.lower() for skill in skills_df['skill'].tolist()]
except Exception as e:
    logging.error(f"Error loading skills dataset: {str(e)}")
    skills_list = []

def extract_skills(text):
    """Extract skills from text using AI, NLP and pattern matching"""
    # First try OpenAI extraction for more accurate results
    if OPENAI_AVAILABLE:
        try:
            openai_skills = extract_skills_with_openai(text)
            if openai_skills and len(openai_skills) > 0:
                logging.info(f"Skills extracted with OpenAI: {openai_skills}")
                return openai_skills
        except Exception as e:
            logging.error(f"Error extracting skills with OpenAI: {str(e)}")
    
    # Fall back to spaCy NLP if OpenAI fails
    if not nlp:
        return fallback_extract_skills(text)
        
    extracted_skills = []
    
    # Use spaCy to process the text
    doc = nlp(text)
    
    # Extract skills using pattern matching with the skills list
    for skill in skills_list:
        # Check if the skill is in the text
        skill_pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(skill_pattern, text, re.IGNORECASE):
            extracted_skills.append(skill)
    
    # Add any potential skills identified by spaCy named entity recognition
    for ent in doc.ents:
        if ent.label_ == "PRODUCT" or ent.label_ == "ORG":
            potential_skill = ent.text.lower()
            # Verify it's a skill by checking against our skill list
            for skill in skills_list:
                if potential_skill == skill.lower() or potential_skill in skill.lower():
                    extracted_skills.append(skill)
                    break
    
    # Extract programming languages and technologies using custom patterns
    tech_patterns = [
        r'\b(Python|Java|C\+\+|JavaScript|HTML|CSS|SQL|PHP|Ruby|Swift|Kotlin|Go|Rust|C#|TypeScript)\b',
        r'\b(React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|TensorFlow|PyTorch|Pandas|NumPy)\b',
        r'\b(AWS|Azure|GCP|Docker|Kubernetes|Git|GitHub|GitLab|Bitbucket|Jenkins|Travis CI|CircleCI)\b'
    ]
    
    for pattern in tech_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            match_lower = match.lower()
            # Check if it's in our skills list
            for skill in skills_list:
                if match_lower == skill.lower():
                    extracted_skills.append(skill)
                    break
    
    # Return unique skills
    return list(set(extracted_skills))

def extract_skills_with_openai(text):
    """Use OpenAI to extract skills from resume text"""
    try:
        logging.info("Extracting skills with OpenAI")
        
        # Construct the prompt for skill extraction
        prompt = f"""
        Extract all professional skills from the following resume text. 
        Focus on technical skills, programming languages, tools, frameworks, methodologies, and soft skills.
        Return only a JSON array of skills, with no other text.
        
        Resume text:
        {text[:4000]}  # Limit text length to avoid token limits
        
        Format the response as a valid JSON array of strings, for example:
        ["Python", "JavaScript", "React", "Data Analysis", "Project Management"]
        """
        
        # Make the OpenAI API call with JSON response format
        response = openai.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a skilled HR professional with expertise in parsing resumes and identifying professional skills."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Extract the skills from the response
        response_content = response.choices[0].message.content
        skills_data = json.loads(response_content)
        
        # The response might be directly a list or in a skills key
        if isinstance(skills_data, list):
            extracted_skills = skills_data
        elif 'skills' in skills_data:
            extracted_skills = skills_data['skills']
        else:
            # Try to find any array in the response
            for key, value in skills_data.items():
                if isinstance(value, list):
                    extracted_skills = value
                    break
            else:
                extracted_skills = []
        
        # Convert all skills to lowercase for consistency
        extracted_skills = [skill.lower() for skill in extracted_skills if skill]
        
        # Return unique skills
        return list(set(extracted_skills))
    except Exception as e:
        logging.error(f"Error in OpenAI skills extraction: {str(e)}")
        return []

def fallback_extract_skills(text):
    """Fallback method to extract skills using regex only"""
    extracted_skills = []
    
    # Extract skills using pattern matching with the skills list
    for skill in skills_list:
        # Check if the skill is in the text
        skill_pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(skill_pattern, text, re.IGNORECASE):
            extracted_skills.append(skill)
    
    return list(set(extracted_skills))

def categorize_skills(skills):
    """Categorize skills into groups"""
    categories = {
        'Programming Languages': ['Python', 'Java', 'C++', 'JavaScript', 'C#', 'TypeScript', 'PHP', 'Ruby', 'Swift', 'Kotlin'],
        'Web Development': ['HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express', 'Django', 'Flask', 'Bootstrap'],
        'Databases': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Oracle', 'Redis', 'Cassandra', 'DynamoDB'],
        'DevOps & Cloud': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'GitHub', 'GitLab'],
        'Data Science': ['NumPy', 'Pandas', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'R', 'MATLAB', 'Tableau', 'Power BI'],
        'Mobile Development': ['Android', 'iOS', 'React Native', 'Flutter', 'Xamarin'],
        'Other': []
    }
    
    categorized = {category: [] for category in categories}
    
    for skill in skills:
        categorized_flag = False
        for category, category_skills in categories.items():
            if any(category_skill.lower() == skill.lower() for category_skill in category_skills):
                categorized[category].append(skill)
                categorized_flag = True
                break
        
        if not categorized_flag:
            categorized['Other'].append(skill)
    
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}

def generate_skill_test_questions(skills):
    """Generate test questions for skills assessment"""
    from utils.openai_helper import generate_skill_questions
    
    questions = []
    
    # Map skills to predefined questions as fallback
    skill_questions = {
        'Python': [
            {
                'question': 'What is the output of the following Python code?\n\nx = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)',
                'options': ['[1, 2, 3]', '[1, 2, 3, 4]', '[4, 1, 2, 3]', 'Error'],
                'answer': '[1, 2, 3, 4]'
            },
            {
                'question': 'Which of the following is NOT a built-in data type in Python?',
                'options': ['List', 'Dictionary', 'Array', 'Tuple'],
                'answer': 'Array'
            },
            {
                'question': 'What is the time complexity of accessing an element in a dictionary?',
                'options': ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'],
                'answer': 'O(1)'
            },
            {
                'question': 'Which of the following is a Python decorator?',
                'options': ['@property', '#include', '$parameter', '&reference'],
                'answer': '@property'
            },
            {
                'question': 'What will be the output of: print(list(filter(lambda x: x > 5, [2, 4, 6, 8, 10])))?',
                'options': ['[6, 8, 10]', '[2, 4]', 'Error', '[2, 4, 6, 8, 10]'],
                'answer': '[6, 8, 10]'
            }
        ],
        'JavaScript': [
            {
                'question': 'What is the output of console.log(1 + "2" + "2");',
                'options': ['122', '32', '14', 'Error'],
                'answer': '122'
            },
            {
                'question': 'Which of the following is NOT a JavaScript framework or library?',
                'options': ['React', 'Vue', 'Django', 'Angular'],
                'answer': 'Django'
            },
            {
                'question': 'What does the "async" keyword do in JavaScript?',
                'options': ['Marks a function as asynchronous', 'Increases execution speed', 'Creates a new thread', 'Blocks execution'],
                'answer': 'Marks a function as asynchronous'
            },
            {
                'question': 'What is the prototype chain in JavaScript?',
                'options': ['A series of objects linked through prototypes', 'A data structure for storing arrays', 'A method for optimizing code', 'A way to encrypt data'],
                'answer': 'A series of objects linked through prototypes'
            },
            {
                'question': 'Which method would you use to create a deep copy of an object in JavaScript?',
                'options': ['JSON.parse(JSON.stringify(obj))', 'Object.assign({}, obj)', 'obj.slice()', 'obj.clone()'],
                'answer': 'JSON.parse(JSON.stringify(obj))'
            }
        ],
        'Java': [
            {
                'question': 'What is the parent class of all classes in Java?',
                'options': ['String', 'System', 'Object', 'Root'],
                'answer': 'Object'
            },
            {
                'question': 'Which of the following is not a valid access modifier in Java?',
                'options': ['public', 'private', 'protected', 'friend'],
                'answer': 'friend'
            },
            {
                'question': 'Which collection in Java provides the fastest lookups?',
                'options': ['HashMap', 'ArrayList', 'LinkedList', 'Vector'],
                'answer': 'HashMap'
            },
            {
                'question': 'What is the purpose of the "volatile" keyword in Java?',
                'options': ['Indicates a variable may be changed by multiple threads', 'Makes a variable unchangeable', 'Optimizes variable access', 'Indicates a critical section'],
                'answer': 'Indicates a variable may be changed by multiple threads'
            },
            {
                'question': 'Which Java construct is used for exception handling?',
                'options': ['try-catch-finally', 'if-else-endif', 'switch-case', 'for-next'],
                'answer': 'try-catch-finally'
            }
        ],
        'HTML': [
            {
                'question': 'Which HTML tag is used to define an internal style sheet?',
                'options': ['<script>', '<style>', '<html>', '<css>'],
                'answer': '<style>'
            },
            {
                'question': 'Which HTML attribute is used to define inline styles?',
                'options': ['styles', 'style', 'class', 'font'],
                'answer': 'style'
            },
            {
                'question': 'What does the "defer" attribute do in a script tag?',
                'options': ['Postpones script execution until page is parsed', 'Loads the script faster', 'Prevents script execution', 'Compresses the script'],
                'answer': 'Postpones script execution until page is parsed'
            },
            {
                'question': 'Which element is used to create a dropdown list?',
                'options': ['<select>', '<dropdown>', '<option>', '<list>'],
                'answer': '<select>'
            },
            {
                'question': 'Which HTML5 element is used to specify a footer for a document or section?',
                'options': ['<footer>', '<bottom>', '<section>', '<end>'],
                'answer': '<footer>'
            }
        ],
        'CSS': [
            {
                'question': 'Which CSS property controls the text size?',
                'options': ['text-size', 'font-size', 'text-style', 'font-style'],
                'answer': 'font-size'
            },
            {
                'question': 'What does CSS stand for?',
                'options': ['Cascading Style Sheets', 'Computer Style Sheets', 'Creative Style Sheets', 'Colorful Style Sheets'],
                'answer': 'Cascading Style Sheets'
            },
            {
                'question': 'Which CSS selector has the highest specificity?',
                'options': ['ID selector', 'Class selector', 'Tag selector', 'Universal selector'],
                'answer': 'ID selector'
            },
            {
                'question': 'What is the purpose of the z-index property?',
                'options': ['Controls stacking order of elements', 'Controls element width', 'Controls element position', 'Controls element visibility'],
                'answer': 'Controls stacking order of elements'
            },
            {
                'question': 'Which unit is relative to the font-size of the element?',
                'options': ['em', 'px', 'cm', 'vh'],
                'answer': 'em'
            }
        ],
        'SQL': [
            {
                'question': 'Which SQL statement is used to extract data from a database?',
                'options': ['GET', 'EXTRACT', 'SELECT', 'OPEN'],
                'answer': 'SELECT'
            },
            {
                'question': 'Which SQL keyword is used to filter results?',
                'options': ['FILTER', 'WHERE', 'LIMIT', 'HAVING'],
                'answer': 'WHERE'
            },
            {
                'question': 'What is a database index used for?',
                'options': ['To improve query performance', 'To store metadata', 'To prevent data corruption', 'To normalize data'],
                'answer': 'To improve query performance'
            },
            {
                'question': 'Which SQL join returns rows when there is a match in both tables?',
                'options': ['INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN'],
                'answer': 'INNER JOIN'
            },
            {
                'question': 'What does ACID stand for in database transactions?',
                'options': ['Atomicity, Consistency, Isolation, Durability', 'Advanced Connection, Integration, Data', 'Automatic, Concurrent, Isolated, Distributed', 'Array, Column, Index, Domain'],
                'answer': 'Atomicity, Consistency, Isolation, Durability'
            }
        ],
        'React.js': [
            {
                'question': 'What function is used to update state in a React class component?',
                'options': ['this.state()', 'this.setState()', 'this.updateState()', 'this.changeState()'],
                'answer': 'this.setState()'
            },
            {
                'question': 'In React, what is used to pass data to a component from outside?',
                'options': ['setState', 'props', 'render', 'PropTypes'],
                'answer': 'props'
            },
            {
                'question': 'What is the purpose of the useEffect hook?',
                'options': ['To perform side effects in function components', 'To create state in class components', 'To optimize rendering', 'To handle form submissions'],
                'answer': 'To perform side effects in function components'
            },
            {
                'question': 'What is React Context used for?',
                'options': ['To share data between components without prop drilling', 'To connect to databases', 'To handle form validation', 'To create animations'],
                'answer': 'To share data between components without prop drilling'
            },
            {
                'question': 'What is a Pure Component in React?',
                'options': ['A component that only renders when props change', 'A component without state', 'A component without JSX', 'A component with no side effects'],
                'answer': 'A component that only renders when props change'
            }
        ]
    }
    
    # Use OpenAI to generate better questions first for each skill
    final_questions = []
    
    for skill in skills:
        try:
            # Try to generate questions using OpenAI first
            ai_questions = generate_skill_questions(skill)
            
            if isinstance(ai_questions, list) and len(ai_questions) > 0:
                # OpenAI returned questions successfully
                for q in ai_questions:
                    final_questions.append({
                        'skill': skill,
                        'question': q['question'],
                        'options': q['options'],
                        'answer': q['answer']
                    })
                continue  # Skip to next skill
        except Exception as e:
            logging.error(f"Error generating OpenAI questions for {skill}: {str(e)}")
            # Continue to fallback
            
        # If OpenAI fails or isn't available, use predefined questions
        for known_skill, qs in skill_questions.items():
            if skill.lower() == known_skill.lower():
                # Add all questions for this skill
                for q in qs:
                    final_questions.append({
                        'skill': skill,
                        'question': q['question'],
                        'options': q['options'],
                        'answer': q['answer']
                    })
                break
    
    # If we have too few questions, add some generic ones
    generic_questions = [
        {
            'skill': 'Problem Solving',
            'question': 'What approach would you take to solve a complex programming problem?',
            'options': [
                'Break it down into smaller components and solve each one',
                'Look for existing solutions online and adapt them',
                'Ask a colleague for help immediately',
                'Try solving the entire problem at once'
            ],
            'answer': 'Break it down into smaller components and solve each one'
        },
        {
            'skill': 'Software Development',
            'question': 'Which development methodology emphasizes adaptive planning and continuous improvement?',
            'options': ['Waterfall', 'Agile', 'Big Bang', 'Critical Path Method'],
            'answer': 'Agile'
        },
        {
            'skill': 'Critical Thinking',
            'question': 'What is the most effective way to validate a solution?',
            'options': [
                'Test it against multiple scenarios and edge cases',
                'Compare it with online solutions',
                'Ask for peer approval',
                'Go with your first instinct'
            ],
            'answer': 'Test it against multiple scenarios and edge cases'
        },
        {
            'skill': 'Project Management',
            'question': 'Which is a key principle of effective technical project management?',
            'options': [
                'Regular communication and progress tracking',
                'Adding more developers to speed up a delayed project',
                'Focusing on documentation over working code',
                'Strictly following the initial plan regardless of changes'
            ],
            'answer': 'Regular communication and progress tracking'
        },
        {
            'skill': 'Version Control',
            'question': 'What is the purpose of branching in version control systems?',
            'options': [
                'To work on features or fixes without affecting the main codebase',
                'To speed up code execution',
                'To compress the codebase',
                'To limit developer access to code'
            ],
            'answer': 'To work on features or fixes without affecting the main codebase'
        }
    ]
    
    # Add generic questions if needed
    if len(final_questions) < 5:
        needed = 5 - len(final_questions)
        final_questions.extend(generic_questions[:needed])
    
    return final_questions[:5]  # Return at most 5 questions
