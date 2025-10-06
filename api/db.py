import os
from supabase import create_client
from dotenv import load_dotenv
import uuid

load_dotenv()

class Database:
    def _init_(self):
        # Try to get from environment variables first
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        # If not found in env, try Streamlit secrets (only works in Streamlit)
        if not self.url or not self.key:
            try:
                import streamlit as st
                self.url = st.secrets.get("SUPABASE_URL", self.url)
                self.key = st.secrets.get("SUPABASE_KEY", self.key)
            except ImportError:
                # Streamlit not available (running in FastAPI)
                pass
        
        # If still not found, raise error
        if not self.url or not self.key:
            raise ValueError(
                "Supabase credentials not found. "
                "Please set SUPABASE_URL and SUPABASE_KEY environment variables "
                "or create a .env file with these values."
            )
        
        self.supabase = create_client(self.url, self.key)
    
    def get_user_profile(self, user_id):
        """Get user profile by ID"""
        try:
            response = self.supabase.table("profiles").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            self._handle_error(f"Error fetching user profile: {e}")
            return None
    
    def create_user_profile(self, user_id, username, email, role):  
        """Create a new user profile"""
        try:
            profile_data = {
                "id": user_id,
                "username": username,
                "email": email,
                "role": role
            }
            response = self.supabase.table("profiles").insert(profile_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            if "violates foreign key constraint" in str(e):
                # If foreign key error, try without the ID (let Supabase generate it)
                try:
                    profile_data = {
                        "username": username,
                        "email": email,
                        "role": role
                    }
                    response = self.supabase.table("profiles").insert(profile_data).execute()
                    if response.data:
                        # Return the generated ID
                        return response.data[0]
                except Exception as e2:
                    self._handle_error(f"Error creating user profile (fallback): {e2}")
                    return None
            self._handle_error(f"Error creating user profile: {e}")
            return None
    
    # Jobseeker operations
    def get_applications(self, user_id):
        """Get all applications for a jobseeker"""
        try:
            response = self.supabase.table("applications").select("*").eq("user_id", user_id).execute()
            return response.data
        except Exception as e:
            self._handle_error(f"Error fetching applications: {e}")
            return []
    
    def add_application(self, user_id, company, role, status, notes=None):
        """Add a new job application"""
        try:
            application_data = {
                "user_id": user_id,
                "company": company,
                "role": role,
                "status": status,
                "notes": notes
            }
            response = self.supabase.table("applications").insert(application_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            self._handle_error(f"Error adding application: {e}")
            return None
    
    def update_application_status(self, application_id, status):
        """Update application status"""
        try:
            response = self.supabase.table("applications").update({"status": status}).eq("id", application_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            self._handle_error(f"Error updating application: {e}")
            return None
    
    def delete_application(self, application_id):
        """Delete an application"""
        try:
            response = self.supabase.table("applications").delete().eq("id", application_id).execute()
            return True
        except Exception as e:
            self._handle_error(f"Error deleting application: {e}")
            return False
    
    # Jobprovider operations
    def get_job_postings(self, user_id):
        """Get all job postings for a jobprovider"""
        try:
            response = self.supabase.table("job_postings").select("*").eq("user_id", user_id).execute()
            return response.data
        except Exception as e:
            self._handle_error(f"Error fetching job postings: {e}")
            return []
    
    def add_job_posting(self, user_id, title, description, requirements, deadline):
        """Add a new job posting"""
        try:
            job_data = {
                "user_id": user_id,
                "title": title,
                "description": description,
                "requirements": requirements,
                "deadline": deadline
            }
            response = self.supabase.table("job_postings").insert(job_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            self._handle_error(f"Error adding job posting: {e}")
            return None
    
    def update_job_posting(self, job_id, **kwargs):
        """Update job posting"""
        try:
            response = self.supabase.table("job_postings").update(kwargs).eq("id", job_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            self._handle_error(f"Error updating job posting: {e}")
            return None
    
    def delete_job_posting(self, job_id):
        """Delete a job posting"""
        try:
            response = self.supabase.table("job_postings").delete().eq("id", job_id).execute()
            return True
        except Exception as e:
            self._handle_error(f"Error deleting job posting: {e}")
            return False
    
    def search_applications(self, user_id, search_term):
        """Search applications by company or role"""
        try:
            response = self.supabase.table("applications").select("*").eq("user_id", user_id).ilike("company", f"%{search_term}%").execute()
            response2 = self.supabase.table("applications").select("*").eq("user_id", user_id).ilike("role", f"%{search_term}%").execute()
            return response.data + response2.data
        except Exception as e:
            self._handle_error(f"Error searching applications: {e}")
            return []
    
    # NEW METHODS FOR JOB SEEKERS TO BROWSE AND APPLY TO JOBS
    
    def get_all_job_postings(self, active_only=True):
        """Get all job postings (for job seekers to browse)"""
        try:
            if active_only:
                response = self.supabase.table("job_postings").select("*, profiles(username, email)").eq("status", "active").execute()
            else:
                response = self.supabase.table("job_postings").select("*, profiles(username, email)").execute()
            return response.data
        except Exception as e:
            self._handle_error(f"Error fetching job postings: {e}")
            return []
    
    def apply_to_job(self, user_id, job_posting_id, cover_letter=None):
        """Apply to a job posting and create the linkage"""
        try:
            # First get the job posting details
            job_response = self.supabase.table("job_postings").select("*, profiles(username)").eq("id", job_posting_id).execute()
            
            if not job_response.data:
                self._handle_error("Job posting not found")
                return None
            
            job = job_response.data[0]
            poster_username = job.get('profiles', {}).get('username', 'Unknown Company')
            
            # Create an application record
            application_data = {
                "user_id": user_id,
                "company": poster_username,
                "role": job['title'],
                "status": "applied",
                "notes": f"Applied to: {job['title']}\nJob Description: {job['description']}\nCover Letter: {cover_letter}" if cover_letter else f"Applied to: {job['title']}\nJob Description: {job['description']}"
            }
            
            application_response = self.supabase.table("applications").insert(application_data).execute()
            
            if application_response.data:
                application_id = application_response.data[0]['id']
                
                # Create the job application linkage
                job_application_data = {
                    "job_posting_id": job_posting_id,
                    "application_id": application_id
                }
                
                linkage_response = self.supabase.table("job_applications").insert(job_application_data).execute()
                
                if linkage_response.data:
                    return application_response.data[0]
            
            return None
            
        except Exception as e:
            self._handle_error(f"Error applying to job: {e}")
            return None
    
    def get_jobs_by_company(self, company_name):
        """Get job postings by company name"""
        try:
            # Since we don't have a company field, we'll search by poster's username
            response = self.supabase.table("job_postings").select("*, profiles(username)").ilike("profiles.username", f"%{company_name}%").execute()
            return response.data
        except Exception as e:
            self._handle_error(f"Error searching jobs by company: {e}")
            return []
    
    def search_job_postings(self, search_term):
        """Search job postings by title or description"""
        try:
            response1 = self.supabase.table("job_postings").select("*, profiles(username)").ilike("title", f"%{search_term}%").execute()
            response2 = self.supabase.table("job_postings").select("*, profiles(username)").ilike("description", f"%{search_term}%").execute()
            return response1.data + response2.data
        except Exception as e:
            self._handle_error(f"Error searching job postings: {e}")
            return []
    
    # NEW METHODS FOR JOB PROVIDERS TO SEE APPLICANTS
    
    def get_applicants_for_job(self, job_posting_id):
        """Get all applicants for a specific job posting - SIMPLIFIED"""
        try:
            # Get the applications linked to this job posting
            linkage_response = self.supabase.table("job_applications")\
                .select("application_id, applied_at")\
                .eq("job_posting_id", job_posting_id)\
                .execute()
            
            if not linkage_response.data:
                return []
            
            applicants_data = []
            for link in linkage_response.data:
                # Get application details
                app_response = self.supabase.table("applications")\
                    .select("*, profiles(username, email)")\
                    .eq("id", link['application_id'])\
                    .execute()
                
                if app_response.data:
                    application = app_response.data[0]
                    applicant_info = {
                        'application_id': link['application_id'],
                        'job_posting_id': job_posting_id,
                        'applied_at': link['applied_at'],
                        'applications': application
                    }
                    applicants_data.append(applicant_info)
            
            return applicants_data
        except Exception as e:
            self._handle_error(f"Error fetching applicants: {e}")
            return []
    
    def get_applicants_for_jobprovider(self, user_id):
        """Get all applicants for all jobs posted by a job provider - SIMPLIFIED"""
        try:
            # First get all job postings by this user
            job_postings = self.supabase.table("job_postings")\
                .select("id, title")\
                .eq("user_id", user_id)\
                .execute()
            
            applicants_data = []
            
            for job in job_postings.data:
                # Get applicants for this job
                job_applicants = self.get_applicants_for_job(job['id'])
                for applicant in job_applicants:
                    applicant['job_title'] = job['title']
                    applicants_data.append(applicant)
            
            return applicants_data
        except Exception as e:
            self._handle_error(f"Error fetching job provider applicants: {e}")
            return []
    
    def _handle_error(self, error_message):
        """Handle errors appropriately for both Streamlit and FastAPI"""
        try:
            import streamlit as st
            st.error(error_message)
        except ImportError:
            # Running in FastAPI - print to console
            print(error_message)