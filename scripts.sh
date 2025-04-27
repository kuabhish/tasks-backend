# # Install dependencies
# pip install -r requirements.txt

# # Create PostgreSQL database (replace 'username' with your PostgreSQL username)
# psql -U username -c "CREATE DATABASE task_tracker;"

# Initialize database migrations
flask db init

# Generate migration script
flask db migrate

# Apply migrations to create tables
flask db upgrade

# Run the Flask application
python run.py