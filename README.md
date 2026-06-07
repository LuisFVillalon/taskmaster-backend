# Task Master Backend
TaskMaster Backend is a backend application of RESTful API's built for 
managing tasks and tags in a task management application. It supports full CRUD 
operations, data validation, and relational associations between tasks and tags.


## Overview
The backend application uses Python as the language, FastAPI as a framework, SQLAlchemy for object-relational
mapping, psycopg2-binary to connect to a PostgreSQL database, Pydantic for data validation, and CORS support
to connect to a frontend,  with the goal to create and use RESTful API's that create, read, update, and delete.

Practiced backend application structure and RESTful APIfundamentals by creating schemas, routers, models, 
implementing CRUD operations to a SQL database and error handling by reading HTTP status codes and error 
messages for invalid requests.

I created this backend application to use it to power a task manager web application. 

Using FastAPI's Swagger UI fast-streamed development by prividing easy access to testing endpoints. 

Hope to implement a journal table to the database to interact with. 

## Features

### Task Management
- **Create Tasks**: Add new tasks with title, description, urgency flag, completion status, and optional due date/time.
- **Read Tasks**: Retrieve all tasks or filter by specific criteria.
- **Update Tasks**: Modify task details (full update) or toggle completion status.
- **Delete Tasks**: Remove tasks by ID.
- **Task Hierarchy**: Create parent-child task relationships using `parent_task_id` for task decomposition.
- **Task Estimation**: Set estimated completion time in hours for planning and tracking.
- **Task Complexity**: Rate task complexity from 1-5 to help with prioritization and sprint planning.
- **Multi-User Support**: Assign tasks to users with `user_id` for scalable team collaboration.
- **Task Properties**: Each task includes title, description, completed status, urgent flag, due date/time, estimated time (hours), complexity rating (1-5), parent task reference, and optional user assignment.

### Tag Management
- **Create Tags**: Add new tags with a unique name and optional color.
- **Read Tags**: Retrieve all tags.
- **Update Tags**: Modify tag name or color.
- **Delete Tags**: Remove tags by ID.
- **Tag Properties**: Each tag has a unique name and optional color for visual organization.

### Task-Tag Associations
- **Many-to-Many Relationships**: Tasks can be associated with multiple tags, and tags can be linked to multiple tasks (e.g., categorize tasks by priority or project).
- **Flexible Organization**: Use tags to group and filter tasks dynamically.

## Tech Stack
- **Language:** Python  
- **Framework:** FastAPI  
- **ORM:** SQLAlchemy  
- **Database:** PostgreSQL  
- **Database Driver:** psycopg2-binary  
- **Data Validation:** Pydantic  
- **Middleware:** CORS (to enable frontend communication)

## Project Structure
```
TaskMaster-Backend/
├── package.json                 # Node.js package configuration (if used for any tooling)
├── README.txt                   # Project documentation
├── requirements.txt             # Python dependencies
└── app/                         # Main application directory
    ├── __init__.py              # Package initialization
    ├── main.py                  # FastAPI application entry point
    ├── __pycache__/             # Python bytecode cache
    ├── crud/                    # Data access layer (CRUD operations)
    │   ├── __init__.py
    │   ├── tag_crud.py          # CRUD functions for tags
    │   ├── task_crud.py         # CRUD functions for tasks
    │   └── __pycache__/
    ├── db/                      # Database configuration
    │   ├── __init__.py
    │   ├── database.py          # Database connection and session setup
    │   └── __pycache__/
    ├── models/                  # SQLAlchemy ORM models
    │   ├── __init__.py
    │   ├── tag_model.py         # Tag model definition
    │   ├── task_model.py        # Task model definition
    │   ├── task_tag_model.py    # Many-to-many association model for tasks and tags
    │   └── __pycache__/
    ├── routers/                 # FastAPI route handlers
    │   ├── __init__.py
    │   ├── tags_router.py       # API endpoints for tag operations
    │   ├── tasks_router.py      # API endpoints for task operations
    │   └── __pycache__/
    └── schemas/                 # Pydantic data validation schemas
        ├── __init__.py
        ├── tag_schema.py        # Tag request/response schemas
        ├── task_schema.py       # Task request/response schemas
        └── __pycache__/
```
## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database (or SQLite for local development)
- pip (Python package installer)

### Installation Steps
1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd TaskMaster-Backend
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/Scripts/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   - Ensure PostgreSQL is running.
   - Create a database named `taskmaster` (or update `DATABASE_URL` accordingly).
   - The application will automatically create tables on startup.

5. **Configure environment variables:**
   Create a `.env` file in the root directory with:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/taskmaster
   ```
   Replace with your PostgreSQL credentials. 

6. **Run the application:**
   ```
   python -m uvicorn app.main:app --reload
   ```
   The server will start at `http://localhost:8000`.

## Environment Variables
- `DATABASE_URL`: Database connection string.
  - Example: `postgresql://user:pass@localhost:5432/taskmaster`

## API Endpoints

The API provides RESTful endpoints for managing tasks and tags. Access the interactive documentation at `http://localhost:8000/docs`.

### Tasks Endpoints
- `GET /get-tasks`: Retrieve all tasks.
- `POST /create-task`: Create a new task (body: TaskCreate schema).
  - New optional fields: `estimated_time` (float, hours), `complexity` (int, 1-5), `parent_task_id` (int), `user_id` (int)
- `PUT /update-task/{task_id}`: Update an existing task (body: TaskCreate schema).
  - Supports updating all task properties including new fields.
  - Validates that `parent_task_id` is a valid existing task and prevents self-reference.
- `PATCH /update-task-status/{task_id}`: Toggle task completion status.
- `DELETE /del-task/{task_id}`: Delete a task by ID.

### Tags Endpoints
- `GET /get-tags`: Retrieve all tags.
- `POST /create-tags`: Create a new tag (body: TagCreate schema).
- `PUT /update-tag/{tag_id}`: Update an existing tag (body: TagCreate schema).
- `DELETE /del-tag/{tag_id}`: Delete a tag by ID.

### Root Endpoint
- `GET /`: Welcome message.

## How to Use
1. Start the server as described in Installation.
2. Visit `http://localhost:8000/docs` for Swagger UI to test endpoints interactively.
3. Integrate with a frontend (e.g., React app on `http://localhost:3000`) via CORS-enabled requests.

## Future Improvements
- Implement a journal table for task history and auditing.
- Add authentication and authorization (e.g., JWT tokens).

## Author
[Luis Fernando Villalon] - Created as a learning project for backend development with FastAPI.
```