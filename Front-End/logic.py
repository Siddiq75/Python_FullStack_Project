import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st

class Analytics:
    @staticmethod
    def get_application_stats(applications):
        """Generate statistics for job applications"""
        if not applications:
            return {
                "total": 0,
                "applied": 0,
                "interview": 0,
                "offer": 0,
                "rejected": 0,
                "success_rate": 0
            }
        
        df = pd.DataFrame(applications)
        total = len(df)
        status_counts = df['status'].value_counts().to_dict()
        
        success_rate = 0
        if total > 0:
            success_rate = round((status_counts.get('offer', 0) / total) * 100, 2)
        
        return {
            "total": total,
            "applied": status_counts.get('applied', 0),
            "interview": status_counts.get('interview', 0),
            "offer": status_counts.get('offer', 0),
            "rejected": status_counts.get('rejected', 0),
            "success_rate": success_rate
        }
    
    @staticmethod
    def create_status_chart(applications):
        """Create a pie chart of application statuses"""
        if not applications:
            return None
        
        df = pd.DataFrame(applications)
        status_counts = df['status'].value_counts()
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Application Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        return fig
    
    @staticmethod
    def create_timeline_chart(applications):
        """Create a timeline of applications"""
        if not applications:
            return None
        
        df = pd.DataFrame(applications)
        df['applied_date'] = pd.to_datetime(df['applied_date'])
        timeline = df.groupby(df['applied_date'].dt.date).size().reset_index(name='count')
        
        fig = px.line(
            timeline,
            x='applied_date',
            y='count',
            title="Applications Timeline",
            markers=True
        )
        fig.update_layout(xaxis_title="Date", yaxis_title="Number of Applications")
        return fig

class Validation:
    @staticmethod
    def validate_application_data(company, role, status):
        """Validate application data"""
        errors = []
        if not company or len(company.strip()) == 0:
            errors.append("Company name is required")
        if not role or len(role.strip()) == 0:
            errors.append("Job role is required")
        if status not in ['applied', 'interview', 'offer', 'rejected']:
            errors.append("Invalid status")
        return errors
    
    @staticmethod
    def validate_job_posting_data(title, description, deadline):
        """Validate job posting data"""
        errors = []
        if not title or len(title.strip()) == 0:
            errors.append("Job title is required")
        if not description or len(description.strip()) == 0:
            errors.append("Job description is required")
        if deadline and deadline < datetime.now().date():
            errors.append("Deadline cannot be in the past")
        return errors

class Notification:
    @staticmethod
    def get_upcoming_followups(applications):
        """Get applications that need follow-up"""
        today = datetime.now().date()
        followups = []
        
        for app in applications:
            applied_date = datetime.strptime(app['applied_date'], '%Y-%m-%d').date() if isinstance(app['applied_date'], str) else app['applied_date']
            days_since_application = (today - applied_date).days
            
            # Suggest follow-up after 7 days for applied status
            if app['status'] == 'applied' and days_since_application >= 7:
                followups.append(app)
            # Suggest follow-up after 3 days for interview status
            elif app['status'] == 'interview' and days_since_application >= 3:
                followups.append(app)
        
        return followups