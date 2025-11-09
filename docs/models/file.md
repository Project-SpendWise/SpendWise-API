# File Model

The File model represents an uploaded file in the SpendWise system, linked to a specific user.

## Schema

### Table: `files`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(36) | Primary Key | UUID v4 identifier |
| `user_id` | String(36) | Foreign Key, Not Null, Indexed | Owner user ID (references users.id) |
| `original_filename` | String(255) | Not Null | Original filename from upload |
| `stored_filename` | String(255) | Not Null | Server-side unique filename |
| `file_path` | String(500) | Not Null | Directory path where file is stored |
| `file_type` | String(10) | Not Null | File extension type (pdf, xlsx, xls, csv, docx) |
| `mime_type` | String(100) | Not Null | MIME type of the file |
| `file_size` | Integer | Not Null | File size in bytes |
| `file_hash` | String(64) | Not Null | SHA-256 hash of file content |
| `processing_status` | String(20) | Not Null, Default: 'pending' | Processing status |
| `description` | Text | Nullable | User-provided description |
| `created_at` | DateTime | Not Null | Upload timestamp |
| `updated_at` | DateTime | Not Null | Last update timestamp |

## Relationships

### User Relationship

- **Foreign Key**: `user_id` references `users.id` with `ON DELETE CASCADE`
- **Relationship**: `file.user` - Access the file's owner
- **Back Reference**: `user.files` - Access all user's files (dynamic query)

**Cascade Behavior:**
- When a user is deleted, all their files are automatically deleted
- This ensures no orphaned file records in the database

## Model Definition

```python
from app import db
from datetime import datetime
import uuid
import os

class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(
        db.String(36),
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)
    processing_status = db.Column(db.String(20), default='pending', nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

## Indexes

For query performance, the following indexes are created:

- `idx_files_user_id`: Index on `user_id` for efficient user file queries
- `idx_files_created_at`: Index on `created_at` for date-based sorting

## Methods

### `__init__(user_id, original_filename, stored_filename, file_path, file_type, mime_type, file_size, file_hash, description=None)`

Constructor for creating a new File instance.

**Parameters:**
- `user_id` (str): Owner user's UUID
- `original_filename` (str): Original uploaded filename
- `stored_filename` (str): Server-side unique filename
- `file_path` (str): Directory path where file is stored
- `file_type` (str): File extension type (pdf, xlsx, xls, csv, docx)
- `mime_type` (str): MIME type
- `file_size` (int): File size in bytes
- `file_hash` (str): SHA-256 hash of file content
- `description` (str, optional): User-provided description

**Example:**

```python
file = File(
    user_id="user-uuid-here",
    original_filename="expenses.pdf",
    stored_filename="abc123_expenses.pdf",
    file_path="/path/to/uploads/2025-11-09/user-id/",
    file_type="pdf",
    mime_type="application/pdf",
    file_size=1024000,
    file_hash="sha256-hash-here",
    description="Monthly expenses report"
)
```

### `to_dict(include_user=False)`

Convert file object to dictionary representation.

**Parameters:**
- `include_user` (bool, optional): Include user information

**Returns:**
- `dict`: File data as dictionary

**Example:**

```python
# Basic file data
file_dict = file.to_dict()
# {
#     'id': '550e8400-e29b-41d4-a716-446655440000',
#     'user_id': 'user-uuid-here',
#     'original_filename': 'expenses.pdf',
#     'stored_filename': 'abc123_expenses.pdf',
#     'file_path': '/path/to/uploads/2025-11-09/user-id/',
#     'file_type': 'pdf',
#     'mime_type': 'application/pdf',
#     'file_size': 1024000,
#     'file_hash': 'sha256-hash-here',
#     'processing_status': 'pending',
#     'description': 'Monthly expenses',
#     'created_at': '2025-11-09T14:00:00Z',
#     'updated_at': '2025-11-09T14:00:00Z'
# }

# Include user information
file_dict = file.to_dict(include_user=True)
# Includes 'user' field with user data
```

### `to_dict_with_user()`

Convert file to dictionary including user information.

**Returns:**
- `dict`: File data with user information

### `update_processing_status(status)`

Update the file's processing status.

**Parameters:**
- `status` (str): New status ('pending', 'processing', 'completed', 'failed')

**Raises:**
- `ValueError`: If status is invalid

**Example:**

```python
file.update_processing_status('processing')
file.update_processing_status('completed')
```

### `get_full_path()`

Get the full filesystem path to the file.

**Returns:**
- `str`: Full path to the file

**Example:**

```python
full_path = file.get_full_path()
# "/path/to/uploads/2025-11-09/user-id/abc123_expenses.pdf"
```

### `exists_on_disk()`

Check if the file exists on the filesystem.

**Returns:**
- `bool`: True if file exists, False otherwise

**Example:**

```python
if file.exists_on_disk():
    print("File is available")
```

## Usage Examples

### Creating a File

```python
from models.file import File
from app import db
from utils.file_utils import generate_file_hash, generate_stored_filename, get_file_storage_path

# After uploading file
user_id = "user-uuid-here"
file_content = b"file content here"
original_filename = "expenses.pdf"

# Generate file metadata
file_hash = generate_file_hash(file_content)
stored_filename = generate_stored_filename(original_filename, user_id)
storage_path, _ = get_file_storage_path(user_id)
mime_type = get_file_mime_type(original_filename)

# Create file record
file = File(
    user_id=user_id,
    original_filename=original_filename,
    stored_filename=stored_filename,
    file_path=storage_path,
    file_type="pdf",
    mime_type=mime_type,
    file_size=len(file_content),
    file_hash=file_hash,
    description="Monthly expenses"
)

db_instance.session.add(file)
db_instance.session.commit()
```

### Querying Files

```python
from models.file import File
from sqlalchemy import select
from flask import current_app

db_instance = current_app.extensions['sqlalchemy']
user_id = "user-uuid-here"

# Get all user's files
files = db_instance.session.scalars(
    select(File).filter_by(user_id=user_id)
).all()

# Get files by type
pdf_files = db_instance.session.scalars(
    select(File).filter_by(user_id=user_id, file_type='pdf')
).all()

# Get single file
file = db_instance.session.get(File, "file-id-here")
```

### Accessing User from File

```python
file = db_instance.session.get(File, "file-id-here")

# Access file owner
user = file.user  # Via backref relationship
print(f"File owner: {user.email}")
```

### Accessing Files from User

```python
from models.user import User

user = db_instance.session.get(User, "user-id-here")

# Get file count
count = user.get_files_count()

# Get files by type
pdf_files = user.get_files_by_type('pdf')

# Query files (dynamic relationship)
recent_files = user.files.order_by(File.created_at.desc()).limit(10).all()
```

## File Storage

Files are stored in a structured directory:
- Base path: `uploads/` (configurable)
- Date folder: `YYYY-MM-DD/`
- User folder: `user_id/`
- Full path: `uploads/2025-11-09/user-id/stored_filename.ext`

## Security

- **Ownership Verification**: All file operations verify `file.user_id == current_user_id`
- **Filename Sanitization**: Original filenames are sanitized to prevent path traversal
- **Unique Filenames**: Stored filenames include UUID to prevent collisions
- **Hash Verification**: SHA-256 hash stored for integrity checking and duplicate detection

## Processing Status

The `processing_status` field tracks file processing state:
- `pending`: File uploaded, awaiting processing
- `processing`: File is currently being processed
- `completed`: Processing completed successfully
- `failed`: Processing failed

This field is reserved for future file processing/extraction features.

## File Types

Supported file types:
- **PDF** (`.pdf`): Portable Document Format
- **XLSX** (`.xlsx`): Excel 2007+ format
- **XLS** (`.xls`): Excel 97-2003 format
- **CSV** (`.csv`): Comma-separated values
- **DOCX** (`.docx`): Word 2007+ format

## File Size Limits

- Maximum file size: 10MB (configurable via `MAX_CONTENT_LENGTH`)
- Empty files are rejected
- File size is stored in bytes

