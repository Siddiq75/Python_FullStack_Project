# Job Application Tracker with Role-Based Access

The Job Application Tracker is a web-based system designed to help users manage job applications efficiently. It provides a role-specific experience for two types of users: Jobseekers and Jobproviders, ensuring personalized dashboards and secure access.


## 🔹 Features

### 👨‍💼 Jobseeker Features

- **Add Job Applications** – Save details like company name, role, application date, and current status.  
- **Update Application Status** – Track progress through stages like Applied → Interview → Offer → Rejected.  
- **Search & Filter** – Quickly find applications by company, role, or status.  
- **Reminder Notifications** – Receive email reminders for follow-ups, interviews, or deadlines.  
- **Dashboard Overview** – View all applications, progress charts, and upcoming deadlines in one place.  
- **Analytics (Optional)** – Visualize success rate, pending applications, or interviews scheduled.  

### 🏢 Jobprovider Features

- **Post New Jobs** – Create job listings with details like role, requirements, and application deadlines.  
- **Manage Job Postings** – Update or delete active job postings easily.  
- **Applicant Tracking (Optional)** – Monitor applications received for each posted job.  
- **Search & Filter Jobs** – Filter postings by status (active/closed) or role.  
- **Dashboard Overview** – See total jobs posted, number of applicants, and status summaries.  
- **Analytics (Optional)** – Track application trends, most applied positions, or top candidates.


## Project Structure
```
Job Application Tracker/
├── api/
│   └── main.py              # API entry point for backend logic
│
├── Front-End/
│   └── app.py               # Frontend application (UI handling)
│
├── src/
│   ├── db.py                # Database connections and schema
│   └── logic.py             # Core business logic for job tracking
│
├── .env                     # Environment variables (API keys, DB URL, etc.)
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
```
## Quick Start

### Prerequisites

- Python 3.8 or higher
- A Supabase account (for database connection)
- Git (for cloning the repository)


### 1. Clone or Download the Project

**Option 1:Clone with Git**
git clone https://github.com/Siddiq75/Python_FullStack_Project.git

cd Python_FullStack_Project

**Option 2: Download ZIP**
Go to the GitHub repository, click Code → Download ZIP, then extract it.

### 2.Set Up a Python Virtual Environment

python -m venv venv       # Create virtual environment

Activate the environment:

venv\Scripts\activate

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Configure Environment Variables

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

### 5.Run the Application

## Streamlit Frontend
streamlit run frontend/app.py

The app will open in your Browser at `http://localhost:8501`

## FastAPI Backend

cd api
python main.py

The app will open in your Browser at `http://localhost:8000`

## 🔹 Technologies Used

This project leverages modern web development tools and frameworks to build a **role-based job application tracker**:

### Frontend
- **Streamlit** – For building interactive dashboards and role-specific user interfaces.

### Backend
- **FastAPI** – Handles API endpoints, authentication, and business logic.
- **Python** – Core programming language for backend and integrations.

### Database & Authentication
- **Supabase (PostgreSQL)** – Stores user profiles, job applications, and job postings.
- **Supabase Auth** – Provides secure authentication and role management.
- **Row-Level Security (RLS)** – Ensures role-based access to data.

### Extras
- **Email Reminders** – Automated notifications for jobseekers using SMTP or email API.
- **Analytics & Dashboards** – Summary statistics and insights for jobseekers and jobproviders.

### Development Tools
- **VS Code / PyCharm** – Code editor for Python and Streamlit development.
- **Git & GitHub** – Version control and repository hosting.


### Key Components

1. **src/db.py**: Database operations  
   - Handles all CRUD operations with Supabase  

2. **src/logic.py**: Business logic  
   - Task validation and processing  


### Troubleshooting

1. **Database Issues (src/db.py)**  
   - **Connection Error**: Ensure Supabase URL and API keys are correctly set in environment variables.  
   - **CRUD Failures**: Check table names and schema in Supabase; mismatched column names can cause errors.  
   - **Timeouts**: Verify network connectivity and Supabase service availability.  

2. **Logic Errors (src/logic.py)**  
   - **Validation Fails**: Make sure input data follows expected schema (e.g., required fields, data types).  
   - **Processing Stops**: Check logs for exceptions; wrap critical sections in `try/except` to capture errors.  
   - **Unexpected Behavior**: Add unit tests to confirm business rules are correctly implemented.  


### Future Enhancements

1. **Database Layer (src/db.py)**  
   - Add caching layer (e.g., Redis) to reduce repeated queries.  
   - Implement advanced query optimization and bulk operations.  
   - Add database migration support for schema evolution.  

2. **Business Logic (src/logic.py)**  
   - Introduce role-based validations for tasks.  
   - Support asynchronous task processing for scalability.  
   - Add detailed logging and monitoring for better debugging.  

    
### Support

If you encounter any issues or have any questions:

Mobile:9392379986
Email id:shaiksiddiq264@gmail.com































