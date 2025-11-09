# File Utilities

The `utils/file_utils.py` module provides file handling utilities for validation, storage, and management.

## Constants

### `ALLOWED_EXTENSIONS`

Set of allowed file extensions:
```python
ALLOWED_EXTENSIONS = {'.pdf', '.xlsx', '.xls', '.csv', '.docx'}
```

### `MIME_TYPES`

Mapping of file extensions to MIME types:
```python
MIME_TYPES = {
    '.pdf': 'application/pdf',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xls': 'application/vnd.ms-excel',
    '.csv': 'text/csv',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}
```

## Functions

### `validate_file_type(filename)`

Validate if file extension is allowed.

**Parameters:**
- `filename` (str): Filename to validate

**Returns:**
- `tuple`: (is_valid: bool, error_message: str | None, file_type: str | None)

**Example:**

```python
from utils.file_utils import validate_file_type

is_valid, error_msg, file_type = validate_file_type("document.pdf")
if is_valid:
    print(f"File type: {file_type}")  # "pdf"
else:
    print(error_msg)
```

---

### `validate_file_size(file_size, max_size=None)`

Validate file size against maximum allowed size.

**Parameters:**
- `file_size` (int): File size in bytes
- `max_size` (int, optional): Maximum size in bytes (defaults to config MAX_CONTENT_LENGTH)

**Returns:**
- `tuple`: (is_valid: bool, error_message: str | None)

**Example:**

```python
from utils.file_utils import validate_file_size

file_size = 5 * 1024 * 1024  # 5MB
is_valid, error_msg = validate_file_size(file_size)
if not is_valid:
    print(error_msg)
```

---

### `generate_file_hash(file_content)`

Generate SHA-256 hash of file content.

**Parameters:**
- `file_content` (bytes): File content as bytes

**Returns:**
- `str`: SHA-256 hash as hexadecimal string

**Example:**

```python
from utils.file_utils import generate_file_hash

with open('file.pdf', 'rb') as f:
    content = f.read()
    file_hash = generate_file_hash(content)
    print(f"Hash: {file_hash}")
```

---

### `generate_stored_filename(original_filename, user_id=None)`

Generate a unique stored filename.

**Format:** `{uuid}_{sanitized_original_filename}.ext`

**Parameters:**
- `original_filename` (str): Original filename
- `user_id` (str, optional): User ID (currently unused but reserved for future use)

**Returns:**
- `str`: Unique stored filename

**Example:**

```python
from utils.file_utils import generate_stored_filename

stored = generate_stored_filename("My Document.pdf")
# "abc12345_My_Document.pdf"
```

---

### `get_file_storage_path(user_id, base_upload_folder=None)`

Generate file storage path: `uploads/YYYY-MM-DD/user_id/`

**Parameters:**
- `user_id` (str): User ID
- `base_upload_folder` (str, optional): Base upload folder (defaults to config UPLOAD_FOLDER)

**Returns:**
- `tuple`: (full_path: str, relative_path: str)

**Example:**

```python
from utils.file_utils import get_file_storage_path

full_path, relative_path = get_file_storage_path("user-123")
# full_path: "/project/uploads/2025-11-09/user-123/"
# relative_path: "uploads/2025-11-09/user-123/"
```

---

### `ensure_directory_exists(directory_path)`

Ensure directory exists, create if it doesn't.

**Parameters:**
- `directory_path` (str): Directory path to ensure exists

**Example:**

```python
from utils.file_utils import ensure_directory_exists

ensure_directory_exists("/path/to/uploads/2025-11-09/user-123/")
```

---

### `save_file(file_content, file_path, filename)`

Save file to disk.

**Parameters:**
- `file_content` (bytes): File content to save
- `file_path` (str): Directory path where file should be saved
- `filename` (str): Filename to use

**Returns:**
- `tuple`: (success: bool, error_message: str | None, full_path: str | None)

**Example:**

```python
from utils.file_utils import save_file, ensure_directory_exists

file_content = b"file content"
file_path = "/path/to/uploads/2025-11-09/user-123/"
filename = "document.pdf"

ensure_directory_exists(file_path)
success, error_msg, full_path = save_file(file_content, file_path, filename)
if success:
    print(f"File saved to: {full_path}")
```

---

### `delete_file_from_disk(file_path)`

Delete file from filesystem.

**Parameters:**
- `file_path` (str): Full path to file to delete

**Returns:**
- `tuple`: (success: bool, error_message: str | None)

**Example:**

```python
from utils.file_utils import delete_file_from_disk

success, error_msg = delete_file_from_disk("/path/to/file.pdf")
if not success:
    print(f"Error: {error_msg}")
```

---

### `get_file_mime_type(filename)`

Get MIME type from filename extension.

**Parameters:**
- `filename` (str): Filename

**Returns:**
- `str`: MIME type

**Example:**

```python
from utils.file_utils import get_file_mime_type

mime_type = get_file_mime_type("document.pdf")
# "application/pdf"
```

---

### `sanitize_filename(filename)`

Sanitize filename to prevent path traversal attacks.

**Parameters:**
- `filename` (str): Filename to sanitize

**Returns:**
- `str`: Sanitized filename

**Example:**

```python
from utils.file_utils import sanitize_filename

safe_name = sanitize_filename("../../../etc/passwd")
# "etc_passwd"
```

---

### `get_file_extension(filename)`

Get file extension without the dot.

**Parameters:**
- `filename` (str): Filename

**Returns:**
- `str`: File extension (without dot)

**Example:**

```python
from utils.file_utils import get_file_extension

ext = get_file_extension("document.pdf")
# "pdf"
```

## Usage in Routes

These utilities are used in file route handlers:

```python
from utils.file_utils import (
    validate_file_type,
    validate_file_size,
    generate_file_hash,
    generate_stored_filename,
    get_file_storage_path,
    save_file
)

# In upload route
file = request.files['file']
file_content = file.read()

# Validate
is_valid, error_msg, file_type = validate_file_type(file.filename)
if not is_valid:
    return error_response(error_msg, 'INVALID_FILE_TYPE', 400)

is_valid, error_msg = validate_file_size(len(file_content))
if not is_valid:
    return error_response(error_msg, 'FILE_TOO_LARGE', 400)

# Generate metadata
file_hash = generate_file_hash(file_content)
stored_filename = generate_stored_filename(file.filename)
storage_path, _ = get_file_storage_path(user_id)

# Save file
success, error_msg, full_path = save_file(file_content, storage_path, stored_filename)
```

## Security Features

1. **Filename Sanitization**: Prevents path traversal attacks
2. **File Type Validation**: Only allows specified file types
3. **Size Validation**: Enforces maximum file size limits
4. **Hash Generation**: SHA-256 for integrity checking and duplicate detection
5. **Unique Filenames**: UUID-based naming prevents collisions

## File Storage Pattern

Files are organized in a structured hierarchy:
- Base: `uploads/` (configurable)
- Date: `YYYY-MM-DD/`
- User: `user_id/`
- File: `stored_filename.ext`

This organization:
- Groups files by upload date
- Separates files by user
- Makes cleanup and management easier
- Supports future date-based archival

