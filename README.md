# Naukri Job Application Automation Script

## Project Overview

This is an automation script designed to streamline the job application process on **Naukri.com**. It automates the tedious task of applying to jobs, saving you time and effort. By processing your resume content and using it to fill out job applications, the script mimics your job profile and submits applications on your behalf. This open-source tool uses Python and can be easily customized to fit your specific job preferences.

## Features

- Automatically applies to jobs on Naukri.com based on your profile and resume.
- Uses AI to process your resume context and respond to job applications on your behalf.
- Saves time and reduces manual effort in the job application process.

## How to Use

### Step 1: Install Required Packages

To get started, install the required Python packages listed in `requirements.txt`. Run the following command in your terminal:
```bash
pip install -r requirements.txt
```
### Step 2: Update your creds
go to .env file and add your creds for `naukri.com` site

### Step 3: Update your JOB Profile
in `apply_job.py` file provide your job profile and in data folder add your resume content in txt format (for AI model to process your resume context to answer on your behalf)

### Step 4: Main Script
run py apply_job.py file
