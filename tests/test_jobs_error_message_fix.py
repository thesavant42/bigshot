"""
Test for verifying the jobs.error_message column fix
"""
import pytest
import tempfile
import sqlite3
import os
from app import create_app, db
from app.models.models import Job
from flask_jwt_extended import create_access_token


class TestJobsErrorMessageFix:
    """Test that the error_message column issue is fixed"""

    def test_job_error_message_column_exists_in_sqlalchemy_model(self):
        """Test that the Job model has the error_message column"""
        # Check that the Job model has the error_message attribute
        assert hasattr(Job, 'error_message'), "Job model should have error_message attribute"
        
        # Check that it's in the to_dict method
        job = Job(type='test', domain='example.com', status='pending')
        job_dict = job.to_dict()
        assert 'error_message' in job_dict, "to_dict() should include error_message field"

    def test_job_error_message_column_in_sqlite_schema(self):
        """Test that the SQLite schema file includes error_message column"""
        schema_path = os.path.join(os.path.dirname(__file__), '../config/schema.sql')
        with open(schema_path, 'r') as f:
            schema_content = f.read()
        
        # Check that the jobs table includes error_message
        assert 'error_message TEXT' in schema_content, "SQLite schema should include error_message column"
        
        # Test creating a database from the schema file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.executescript(schema_content)
            conn.commit()
            
            # Check that the error_message column exists
            cursor.execute('PRAGMA table_info(jobs)')
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            assert 'error_message' in column_names, f"error_message column missing from schema. Found: {column_names}"
            conn.close()
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_job_error_message_column_in_postgresql_schema(self):
        """Test that the PostgreSQL schema file includes error_message column"""
        project_root = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(project_root, '..', 'config', 'postgresql_schema.sql')
        with open(schema_path, 'r') as f:
            schema_content = f.read()
        
        # Check that the jobs table includes error_message
        assert 'error_message TEXT' in schema_content, "PostgreSQL schema should include error_message column"

    def test_jobs_api_with_error_message(self, app, auth_token):
        """Test that the jobs API works with error_message column"""
        with app.app_context():
            # Create a job with an error message
            job = Job(
                type='test_job',
                domain='example.com',
                status='failed',
                progress=50,
                result='{"error": "Something went wrong"}',
                error_message='Test error message from API test'
            )
            
            db.session.add(job)
            db.session.commit()
            job_id = job.id
            
            # Test the jobs list API
            client = app.test_client()
            headers = {'Authorization': f'Bearer {auth_token}'}
            
            response = client.get('/api/v1/jobs', headers=headers)
            assert response.status_code == 200, f"Jobs API failed: {response.get_data(as_text=True)}"
            
            data = response.get_json()
            assert 'data' in data, "Response should include data field"
            jobs = data['data']
            assert len(jobs) > 0, "Should have at least one job"
            
            # Check that the error_message is included in the response
            job_data = next((j for j in jobs if j['id'] == job_id), None)
            assert job_data is not None, f"Job {job_id} not found in response"
            assert 'error_message' in job_data, "Job data should include error_message field"
            assert job_data['error_message'] == 'Test error message from API test', \
                f"Expected error message, got: {job_data.get('error_message')}"

    def test_job_model_schema_compatibility(self, app):
        """Test that Job model and database schema are compatible"""
        with app.app_context():
            # This test ensures that creating a job with all model fields works
            job = Job(
                type='compatibility_test',
                domain='test.example.com',
                status='completed',
                progress=100,
                result='{"status": "success"}',
                error_message='No errors occurred'
            )
            
            # Should be able to add and commit without errors
            db.session.add(job)
            db.session.commit()
            
            # Should be able to query and convert to dict
            retrieved_job = Job.query.filter_by(id=job.id).first()
            assert retrieved_job is not None, "Job should be retrievable"
            
            job_dict = retrieved_job.to_dict()
            expected_fields = ['id', 'type', 'domain', 'status', 'progress', 'result', 'error_message', 'created_at', 'updated_at']
            
            for field in expected_fields:
                assert field in job_dict, f"Job dict should include {field} field"
            
            assert job_dict['error_message'] == 'No errors occurred', \
                f"Error message should be preserved, got: {job_dict['error_message']}"


# Fixtures for testing
@pytest.fixture
def app():
    """Create a test Flask app"""
    import os
    import tempfile
    
    # Create a temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Set test configuration
    os.environ['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
    os.environ['TESTING'] = 'True'
    
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    # Clean up
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def auth_token(app):
    """Create a JWT token for testing"""
    with app.app_context():
        from app.models.models import User
        user = User.query.filter_by(username='admin').first()
        if user:
            return create_access_token(identity=user.username)
        return None