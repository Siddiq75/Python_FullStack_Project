import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import time
import uuid
from db import Database
from logic import Analytics, Validation, Notification

# Page configuration
st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = Database()

# Authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None

# CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stats-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success-rate {
        color: #00cc96;
        font-weight: bold;
    }
    .warning {
        color: #ffa15a;
        font-weight: bold;
    }
    .job-posting {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .applicant-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def login_page():
    """Login/Signup page"""
    st.markdown('<div class="main-header">💼 Job Application Tracker</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_btn"):
            # Simplified authentication - in production, use proper auth
            if email and password:
                # Generate a proper UUID instead of simple string
                user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, email))
                st.session_state.user_id = user_id
                st.session_state.authenticated = True
                
                # Get or create user profile
                profile = db.get_user_profile(user_id)
                if not profile:
                    username = email.split('@')[0]
                    role = st.selectbox("Select your role", ["jobseeker", "jobprovider"], key="login_role")
                    profile = db.create_user_profile(user_id, username, email, role)
                
                if profile:
                    st.session_state.user_profile = profile
                    st.session_state.user_role = profile['role']
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to create user profile. Please try again.")
            else:
                st.error("Please enter email and password")
    
    with tab2:
        st.subheader("Create New Account")
        username = st.text_input("Username", key="signup_username")
        email = st.text_input("Email", key="signup_email")
        role = st.selectbox("I am a", ["jobseeker", "jobprovider"], key="signup_role")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        if st.button("Create Account", key="signup_btn"):
            if email and username and password and role:
                if password == confirm_password:
                    # Generate a proper UUID
                    user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, email))
                    profile = db.create_user_profile(user_id, username, email, role)
                    if profile:
                        st.session_state.user_id = user_id
                        st.session_state.authenticated = True
                        st.session_state.user_profile = profile
                        st.session_state.user_role = role
                        st.success("Account created successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to create account. Please try again.")
                else:
                    st.error("Passwords do not match")
            else:
                st.error("Please fill all fields")

def jobseeker_dashboard():
    """Jobseeker dashboard"""
    st.title("👨‍💼 Jobseeker Dashboard")
    
    # Quick stats
    applications = db.get_applications(st.session_state.user_id)
    stats = Analytics.get_application_stats(applications)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Applications", stats['total'])
    with col2:
        st.metric("Applied", stats['applied'])
    with col3:
        st.metric("Interviews", stats['interview'])
    with col4:
        st.metric("Offers", stats['offer'])
    with col5:
        st.metric("Success Rate", f"{stats['success_rate']}%")
    
    # Main content - ADDED "Browse Jobs" TAB
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Browse Jobs", "My Applications", "Add Application", "Analytics", "Follow-ups"])
    
    # NEW TAB: Browse Jobs (as first tab)
    with tab1:
        st.subheader("📋 Available Job Postings")
        
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("Search jobs by title or description")
        with col2:
            show_active_only = st.checkbox("Show active only", value=True)
        
        # Get job postings
        if search_term:
            job_postings = db.search_job_postings(search_term)
        else:
            job_postings = db.get_all_job_postings(active_only=show_active_only)
        
        if job_postings:
            st.success(f"Found {len(job_postings)} job postings")
            
            for job in job_postings:
                with st.container():
                    st.markdown(f"""
                    <div class="job-posting">
                        <h3>🏢 {job['title']}</h3>
                        <p><strong>Posted by:</strong> {job.get('profiles', {}).get('username', 'Unknown Company')}</p>
                        <p><strong>Status:</strong> {job['status'].title()}</p>
                        <p><strong>Deadline:</strong> {job['deadline']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("View Details & Apply"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Description:** {job['description']}")
                            st.write(f"**Requirements:** {job['requirements']}")
                            st.write(f"**Posted on:** {job['created_at'].split('T')[0] if 'T' in str(job['created_at']) else job['created_at']}")
                        
                        with col2:
                            st.write("### Apply Now")
                            cover_letter = st.text_area(
                                "Cover Letter (optional)", 
                                key=f"cover_{job['id']}", 
                                height=100,
                                placeholder="Why are you interested in this position?"
                            )
                            
                            if st.button("Submit Application", key=f"apply_{job['id']}"):
                                if cover_letter.strip() == "":
                                    cover_letter = "No cover letter provided"
                                
                                application = db.apply_to_job(
                                    st.session_state.user_id, 
                                    job['id'], 
                                    cover_letter
                                )
                                if application:
                                    st.success("✅ Application submitted successfully!")
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to submit application")
        else:
            st.info("No job postings found. Check back later or try a different search term.")
    
    # Existing tabs (renumbered)
    with tab2:
        st.subheader("My Job Applications")
        
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("Search applications", key="search_apps")
        with col2:
            status_filter = st.selectbox("Filter by status", ["All", "applied", "interview", "offer", "rejected"], key="status_filter")
        
        if search_term:
            display_apps = db.search_applications(st.session_state.user_id, search_term)
        else:
            display_apps = applications
        
        if status_filter != "All":
            display_apps = [app for app in display_apps if app['status'] == status_filter]
        
        if display_apps:
            for app in display_apps:
                with st.expander(f"{app['company']} - {app['role']} ({app['status'].title()})"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**Applied on:** {app['applied_date']}")
                        if app.get('notes'):
                            st.write(f"**Notes:** {app['notes']}")
                    with col2:
                        new_status = st.selectbox(
                            "Update Status",
                            ["applied", "interview", "offer", "rejected"],
                            index=["applied", "interview", "offer", "rejected"].index(app['status']),
                            key=f"status_{app['id']}"
                        )
                        if new_status != app['status']:
                            if st.button("Update", key=f"update_{app['id']}"):
                                if db.update_application_status(app['id'], new_status):
                                    st.success("Status updated!")
                                    time.sleep(1)
                                    st.rerun()
                    with col3:
                        if st.button("Delete", key=f"delete_{app['id']}"):
                            if db.delete_application(app['id']):
                                st.success("Application deleted!")
                                time.sleep(1)
                                st.rerun()
        else:
            st.info("No applications found")
    
    with tab3:
        st.subheader("Add New Application")
        with st.form("add_application"):
            company = st.text_input("Company Name *")
            job_role = st.text_input("Job Role *")
            status = st.selectbox("Status", ["applied", "interview", "offer", "rejected"])
            applied_date = st.date_input("Applied Date", value=date.today())
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Add Application"):
                errors = Validation.validate_application_data(company, job_role, status)
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    application = db.add_application(
                        st.session_state.user_id, company, job_role, status, notes
                    )
                    if application:
                        st.success("Application added successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to add application")
    
    with tab4:
        st.subheader("Application Analytics")
        if applications:
            col1, col2 = st.columns(2)
            with col1:
                fig = Analytics.create_status_chart(applications)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Chart not available - using simple display")
                    status_counts = {}
                    for app in applications:
                        status = app.get('status', 'applied')
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    st.bar_chart(status_counts)
            
            with col2:
                fig2 = Analytics.create_timeline_chart(applications)
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Timeline chart not available")
            
            st.subheader("Detailed Statistics")
            try:
                df = pd.DataFrame(applications)
                st.dataframe(df[['company', 'role', 'status', 'applied_date', 'notes']])
            except:
                for app in applications:
                    st.write(f"**{app['company']}** - {app['role']} ({app['status']})")
        else:
            st.info("No applications to analyze")
    
    with tab5:
        st.subheader("Follow-up Reminders")
        followups = Notification.get_upcoming_followups(applications)
        if followups:
            st.warning(f"You have {len(followups)} applications that need follow-up:")
            for app in followups:
                st.write(f"**{app['company']}** - {app['role']} (Applied on: {app['applied_date']})")
        else:
            st.success("No pending follow-ups! 🎉")

def jobprovider_dashboard():
    """Jobprovider dashboard"""
    st.title("🏢 Job Provider Dashboard")
    
    # Quick stats
    job_postings = db.get_job_postings(st.session_state.user_id)
    total_jobs = len(job_postings) if job_postings else 0
    active_jobs = len([job for job in job_postings if job.get('status') == 'active']) if job_postings else 0
    
    # Get applicant count
    applicants_data = db.get_applicants_for_jobprovider(st.session_state.user_id)
    total_applicants = len(applicants_data)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Job Postings", total_jobs)
    with col2:
        st.metric("Active Postings", active_jobs)
    with col3:
        st.metric("Closed Postings", total_jobs - active_jobs)
    with col4:
        st.metric("Total Applicants", total_applicants)
    
    # Main content - ADD "Applicants" TAB
    tab1, tab2, tab3, tab4 = st.tabs(["My Job Postings", "Applicants", "Add New Job", "Manage Postings"])
    
    with tab1:
        st.subheader("My Job Postings")
        if job_postings:
            for job in job_postings:
                with st.expander(f"{job.get('title', 'Untitled')} ({job.get('status', 'active').title()})"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Description:** {job.get('description', 'No description')}")
                        st.write(f"**Requirements:** {job.get('requirements', 'No requirements')}")
                        st.write(f"**Deadline:** {job.get('deadline', 'No deadline')}")
                        st.write(f"**Created:** {job.get('created_at', 'Unknown')}")
                        
                        # Show applicant count for this job
                        job_applicants = [app for app in applicants_data if app.get('job_posting_id') == job['id']]
                        st.write(f"**Applicants:** {len(job_applicants)}")
                        
                    with col2:
                        current_status = job.get('status', 'active')
                        new_status = st.selectbox(
                            "Status",
                            ["active", "closed"],
                            index=0 if current_status == 'active' else 1,
                            key=f"job_status_{job['id']}"
                        )
                        if new_status != current_status:
                            if st.button("Update Status", key=f"update_job_{job['id']}"):
                                if db.update_job_posting(job['id'], status=new_status):
                                    st.success("Status updated!")
                                    time.sleep(1)
                                    st.rerun()
                        if st.button("Delete", key=f"delete_job_{job['id']}"):
                            if db.delete_job_posting(job['id']):
                                st.success("Job posting deleted!")
                                time.sleep(1)
                                st.rerun()
        else:
            st.info("No job postings yet")
    
    # NEW TAB: Applicants
    with tab2:
        st.subheader("📋 Job Applicants")
        
        if applicants_data:
            st.success(f"You have {total_applicants} applicants across all your job postings")
            
            # Group by job posting
            jobs_with_applicants = {}
            for applicant in applicants_data:
                job_id = applicant['job_posting_id']
                if job_id not in jobs_with_applicants:
                    jobs_with_applicants[job_id] = {
                        'job_title': applicant.get('job_title', 'Unknown Job'),
                        'applicants': []
                    }
                jobs_with_applicants[job_id]['applicants'].append(applicant)
            
            for job_id, job_data in jobs_with_applicants.items():
                with st.expander(f"📝 {job_data['job_title']} - {len(job_data['applicants'])} applicants"):
                    for applicant in job_data['applicants']:
                        st.markdown('<div class="applicant-card">', unsafe_allow_html=True)
                        
                        app_data = applicant.get('applications', {})
                        profile_data = app_data.get('profiles', {})
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**👤 Applicant:** {profile_data.get('username', 'Unknown')}")
                            st.write(f"**📧 Email:** {profile_data.get('email', 'Unknown')}")
                            st.write(f"**📅 Applied on:** {applicant.get('applied_at', 'Unknown')}")
                            st.write(f"**📊 Status:** {app_data.get('status', 'applied').title()}")
                            
                            # Show cover letter/notes
                            notes = app_data.get('notes', '')
                            if notes:
                                with st.expander("View Application Details"):
                                    st.write(notes)
                        
                        with col2:
                            # Job provider can update application status
                            current_status = app_data.get('status', 'applied')
                            new_status = st.selectbox(
                                "Update Status",
                                ["applied", "interview", "offer", "rejected"],
                                index=["applied", "interview", "offer", "rejected"].index(current_status) if current_status in ["applied", "interview", "offer", "rejected"] else 0,
                                key=f"app_status_{app_data.get('id')}"
                            )
                            if new_status != current_status:
                                if st.button("Update", key=f"update_app_{app_data.get('id')}"):
                                    if db.update_application_status(app_data.get('id'), new_status):
                                        st.success("Application status updated!")
                                        time.sleep(1)
                                        st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No applicants yet. Applicants will appear here when job seekers apply to your postings.")
    
    with tab3:
        st.subheader("Add New Job Posting")
        with st.form("add_job_posting"):
            title = st.text_input("Job Title *")
            description = st.text_area("Job Description *")
            requirements = st.text_area("Requirements *")
            deadline = st.date_input("Application Deadline")
            
            if st.form_submit_button("Create Job Posting"):
                errors = Validation.validate_job_posting_data(title, description, deadline)
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    job = db.add_job_posting(
                        st.session_state.user_id, title, description, 
                        requirements, deadline.isoformat()
                    )
                    if job:
                        st.success("Job posting created successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to create job posting")
    
    with tab4:
        st.subheader("Manage Job Postings")
        if job_postings:
            st.info("Use the 'My Job Postings' tab to manage individual postings")
        else:
            st.info("No job postings to manage")

def main():
    """Main application"""
    if not st.session_state.authenticated:
        login_page()
    else:
        # Sidebar with user info
        with st.sidebar:
            if st.session_state.user_profile:
                st.title(f"Welcome, {st.session_state.user_profile.get('username', 'User')}!")
                st.write(f"Role: {st.session_state.user_role.title() if st.session_state.user_role else 'Unknown'}")
                st.write(f"Email: {st.session_state.user_profile.get('email', 'Unknown')}")
                
                # Quick actions based on role
                if st.session_state.user_role == 'jobseeker':
                    st.write("---")
                    st.subheader("Quick Actions")
                    if st.button("Browse Available Jobs"):
                        st.info("Go to the 'Browse Jobs' tab to see available positions")
                
                elif st.session_state.user_role == 'jobprovider':
                    st.write("---")
                    st.subheader("Quick Actions")
                    if st.button("Create New Job Posting"):
                        st.info("Go to the 'Add New Job' tab to create a posting")
                    if st.button("View Applicants"):
                        st.info("Go to the 'Applicants' tab to see who applied")
                        
            else:
                st.title("Welcome!")
                st.write("User profile not loaded")
            
            st.write("---")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.user_role = None
                st.session_state.user_profile = None
                st.rerun()
        
        # Show appropriate dashboard based on role
        if st.session_state.user_role == 'jobseeker':
            jobseeker_dashboard()
        elif st.session_state.user_role == 'jobprovider':
            jobprovider_dashboard()
        else:
            st.error("Invalid user role. Please contact support.")

if __name__ == "__main__":
    main()