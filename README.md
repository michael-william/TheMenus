# Flask Starter

This repository serves as a starter template for creating new Flask projects. Follow the steps below to quickly spin up a new project using this template.

How to Use This Template

## 1. Clone the Starter Repository

- Clone this repository to start a new project: 

        git clone https://github.com/michael-william/Flask-NoCo-S3.git new_project_name
- Replace new_project_name with the name of your new project directory.

## 2. Navigate to the New Project Directory

- Change into the new project directory: 
    
        cd new_project_name

## 3. Remove Git History

- Since this is a new project, remove the Git history of the starter package:

        rm -rf .git

## 4. Initialize a New Git Repository

- Create a fresh Git repository for your new project:

        git init

- Add all files and make an initial commit:

        git add .
        git commit -m "Initial commit for new project"

## 5. Set Up a New Remote (Optional)

- If you want to push your new project to a GitHub repository:
	1.	Create a new repository on GitHub.
	2.	Link your local repository to the new GitHub repository:

            git remote add origin https://github.com/your-username/new-project-repo.git
            git branch -M main
            git push -u origin main

## 6. Customize the Project

1.	Update the project name and description in README.md.
2.	Replace placeholder values in your project (e.g., SECRET_KEY, database URI).
3.	Add new routes, templates, or functionality as needed.

## 7. Install Dependencies

- Set up a virtual environment and install the required dependencies:

        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        pip install -r requirements.txt

## 8. Run the Application

Start the Flask application:

flask run

Features

	•	Flask App Factory Pattern
	•	NoCo DB Integration
    •	MinIO(S3) Integration
	•	WTForms for Forms
	•	Customizable Starter Templates
	•	Static File Organization

You now have a fresh Flask project initialized and ready for development. Feel free to build your app from here!