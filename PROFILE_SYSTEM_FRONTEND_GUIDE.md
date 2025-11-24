# Profile System - Frontend Integration Guide

## Overview

The SpendWise backend now supports a **Profile System** where each uploaded file/statement becomes a selectable "profile". Users can:
- Upload files with profile metadata (name, description, account type, bank name, color, icon)
- Select a profile to view transactions and analytics specific to that profile
- Manage profiles (update metadata, set default profile)
- Keep transactions from different profiles separate

## Database Migration

### Step 1: Run the Migration Script

Before using the profile system, you need to add the new profile columns to the existing `statements` table.

**Run this command:**
```bash
python migrate_add_profile_fields.py
```

**What it does:**
- Adds 7 new columns to the `statements` table:
  - `profile_name` (VARCHAR 255)
  - `profile_description` (TEXT)
  - `account_type` (VARCHAR 100)
  - `bank_name` (VARCHAR 255)
  - `color` (VARCHAR 7) - Hex color code
  - `icon` (VARCHAR 50) - Icon identifier
  - `is_default` (BOOLEAN)
- Updates existing statements with `profile_name = file_name` as default

**Note:** The migration is safe to run multiple times - it checks if columns already exist.

## API Endpoints

### 1. Upload Statement with Profile Metadata

**Endpoint:** `POST /api/statements/upload`

**Request Format:** `multipart/form-data`

**Form Fields:**
- `file` (required) - The statement file
- `profileName` (optional) - User-friendly profile name (e.g., "Personal Account")
- `profileDescription` (optional) - Description of the profile
- `accountType` (optional) - Type of account (e.g., "Checking", "Savings", "Credit Card", "Business")
- `bankName` (optional) - Name of the bank/institution
- `color` (optional) - Hex color code (e.g., "#FF5733")
- `icon` (optional) - Icon identifier (e.g., "wallet", "credit-card", "building")

**Example Request (JavaScript):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('profileName', 'Personal Checking Account');
formData.append('profileDescription', 'My main checking account');
formData.append('accountType', 'Checking');
formData.append('bankName', 'Ziraat Bankası');
formData.append('color', '#3B82F6');
formData.append('icon', 'wallet');

const response = await fetch('http://localhost:5000/api/statements/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
});

const result = await response.json();
```

**Response:**
```json
{
  "data": {
    "id": "statement_123",
    "fileName": "statement.pdf",
    "uploadDate": "2024-01-15T10:30:00Z",
    "status": "processing",
    "transactionCount": 0,
    "statementPeriodStart": null,
    "statementPeriodEnd": null,
    "isProcessed": false,
    "profileName": "Personal Checking Account",
    "profileDescription": "My main checking account",
    "accountType": "Checking",
    "bankName": "Ziraat Bankası",
    "color": "#3B82F6",
    "icon": "wallet",
    "isDefault": true
  },
  "message": "Statement uploaded successfully",
  "statusCode": 200
}
```

**Business Logic:**
- If `profileName` is not provided, it's auto-generated from the filename
- If this is the user's first profile, `isDefault` is automatically set to `true`
- The statement status starts as "processing" and changes to "processed" when transactions are generated

---

### 2. List All Statements (with Profile Info)

**Endpoint:** `GET /api/statements`

**Query Parameters:** None

**Example Request:**
```javascript
const response = await fetch('http://localhost:5000/api/statements', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const result = await response.json();
```

**Response:**
```json
{
  "data": {
    "statements": [
      {
        "id": "statement_123",
        "fileName": "statement.pdf",
        "uploadDate": "2024-01-15T10:30:00Z",
        "status": "processed",
        "transactionCount": 45,
        "statementPeriodStart": "2023-12-15T00:00:00Z",
        "statementPeriodEnd": "2024-01-15T23:59:59Z",
        "isProcessed": true,
        "profileName": "Personal Checking Account",
        "profileDescription": "My main checking account",
        "accountType": "Checking",
        "bankName": "Ziraat Bankası",
        "color": "#3B82F6",
        "icon": "wallet",
        "isDefault": true
      },
      {
        "id": "statement_456",
        "fileName": "business_statement.pdf",
        "uploadDate": "2024-01-10T14:20:00Z",
        "status": "processed",
        "transactionCount": 32,
        "statementPeriodStart": "2023-12-10T00:00:00Z",
        "statementPeriodEnd": "2024-01-10T23:59:59Z",
        "isProcessed": true,
        "profileName": "Business Account",
        "profileDescription": null,
        "accountType": "Business",
        "bankName": "İş Bankası",
        "color": "#10B981",
        "icon": "building",
        "isDefault": false
      }
    ]
  },
  "statusCode": 200
}
```

**Business Logic:**
- Statements are sorted by `isDefault DESC, uploadDate DESC` (default profile first, then newest first)
- Use this endpoint to populate a profile selection dropdown

---

### 3. Get Statement Details

**Endpoint:** `GET /api/statements/{id}`

**Example Request:**
```javascript
const statementId = 'statement_123';
const response = await fetch(`http://localhost:5000/api/statements/${statementId}`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const result = await response.json();
```

**Response:** Same format as individual statement object in the list endpoint.

---

### 4. List Profiles (Simplified)

**Endpoint:** `GET /api/statements/profiles`

**Purpose:** Returns a simplified list of profiles optimized for profile selection dropdowns.

**Example Request:**
```javascript
const response = await fetch('http://localhost:5000/api/statements/profiles', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const result = await response.json();
```

**Response:**
```json
{
  "data": {
    "profiles": [
      {
        "id": "statement_123",
        "profileName": "Personal Checking Account",
        "accountType": "Checking",
        "bankName": "Ziraat Bankası",
        "color": "#3B82F6",
        "icon": "wallet",
        "isDefault": true,
        "transactionCount": 45,
        "status": "processed"
      },
      {
        "id": "statement_456",
        "profileName": "Business Account",
        "accountType": "Business",
        "bankName": "İş Bankası",
        "color": "#10B981",
        "icon": "building",
        "isDefault": false,
        "transactionCount": 32,
        "status": "processed"
      }
    ]
  },
  "statusCode": 200
}
```

**Business Logic:**
- Use this endpoint specifically for profile selection UI components
- Profiles are sorted by `isDefault DESC, uploadDate DESC`
- Only includes essential fields needed for selection

---

### 5. Update Profile Metadata

**Endpoint:** `PUT /api/statements/{id}/profile`

**Request Body:** JSON (all fields optional)

**Example Request:**
```javascript
const statementId = 'statement_123';
const response = await fetch(`http://localhost:5000/api/statements/${statementId}/profile`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    profileName: 'Updated Profile Name',
    profileDescription: 'Updated description',
    accountType: 'Savings',
    bankName: 'Updated Bank Name',
    color: '#EF4444',
    icon: 'credit-card'
  })
});

const result = await response.json();
```

**Response:**
```json
{
  "data": {
    "id": "statement_123",
    "fileName": "statement.pdf",
    "uploadDate": "2024-01-15T10:30:00Z",
    "status": "processed",
    "transactionCount": 45,
    "profileName": "Updated Profile Name",
    "profileDescription": "Updated description",
    "accountType": "Savings",
    "bankName": "Updated Bank Name",
    "color": "#EF4444",
    "icon": "credit-card",
    "isDefault": true
  },
  "message": "Profile updated successfully",
  "statusCode": 200
}
```

**Business Logic:**
- Only provided fields are updated
- Empty strings are converted to `null`
- All fields are optional

---

### 6. Set Default Profile

**Endpoint:** `POST /api/statements/{id}/set-default`

**Example Request:**
```javascript
const statementId = 'statement_456';
const response = await fetch(`http://localhost:5000/api/statements/${statementId}/set-default`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const result = await response.json();
```

**Response:**
```json
{
  "data": {
    "id": "statement_456",
    "profileName": "Business Account",
    "isDefault": true,
    // ... other fields
  },
  "message": "Default profile set successfully",
  "statusCode": 200
}
```

**Business Logic:**
- Sets `isDefault=true` for the specified profile
- Automatically sets `isDefault=false` for all other user profiles
- Only one profile can be default at a time

---

### 7. Delete Profile

**Endpoint:** `POST /api/statements/{id}/delete`

**Note:** This is the existing delete endpoint. It deletes the statement and all associated transactions.

**Example Request:**
```javascript
const statementId = 'statement_123';
const response = await fetch(`http://localhost:5000/api/statements/${statementId}/delete`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const result = await response.json();
```

---

## Frontend Business Logic Implementation

### 1. Profile Selection Flow

**Step 1: Load Profiles on App Start**
```javascript
async function loadProfiles() {
  try {
    const response = await fetch('http://localhost:5000/api/statements/profiles', {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    const result = await response.json();
    const profiles = result.data.profiles;
    
    // Store in state/context
    setProfiles(profiles);
    
    // Auto-select default profile if exists
    const defaultProfile = profiles.find(p => p.isDefault);
    if (defaultProfile) {
      setSelectedProfile(defaultProfile);
    } else if (profiles.length > 0) {
      // If no default, select first profile
      setSelectedProfile(profiles[0]);
    }
  } catch (error) {
    console.error('Failed to load profiles:', error);
  }
}
```

**Step 2: Profile Selection Dropdown Component**
```javascript
function ProfileSelector({ profiles, selectedProfile, onProfileChange }) {
  return (
    <select 
      value={selectedProfile?.id || ''} 
      onChange={(e) => {
        const profile = profiles.find(p => p.id === e.target.value);
        onProfileChange(profile);
      }}
    >
      {profiles.map(profile => (
        <option key={profile.id} value={profile.id}>
          {profile.profileName} {profile.isDefault && '(Default)'}
        </option>
      ))}
    </select>
  );
}
```

**Step 3: Filter Transactions by Selected Profile**
```javascript
async function loadTransactions(selectedProfileId) {
  try {
    const url = selectedProfileId 
      ? `http://localhost:5000/api/transactions?statementId=${selectedProfileId}`
      : 'http://localhost:5000/api/transactions';
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    const result = await response.json();
    return result.data.transactions;
  } catch (error) {
    console.error('Failed to load transactions:', error);
    return [];
  }
}
```

---

### 2. File Upload with Profile Metadata

**Upload Form Component:**
```javascript
function StatementUploadForm({ onUploadSuccess }) {
  const [formData, setFormData] = useState({
    profileName: '',
    profileDescription: '',
    accountType: '',
    bankName: '',
    color: '#3B82F6',
    icon: 'wallet'
  });
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert('Please select a file');
      return;
    }

    setUploading(true);
    const uploadFormData = new FormData();
    uploadFormData.append('file', file);
    
    // Add profile metadata if provided
    if (formData.profileName) {
      uploadFormData.append('profileName', formData.profileName);
    }
    if (formData.profileDescription) {
      uploadFormData.append('profileDescription', formData.profileDescription);
    }
    if (formData.accountType) {
      uploadFormData.append('accountType', formData.accountType);
    }
    if (formData.bankName) {
      uploadFormData.append('bankName', formData.bankName);
    }
    if (formData.color) {
      uploadFormData.append('color', formData.color);
    }
    if (formData.icon) {
      uploadFormData.append('icon', formData.icon);
    }

    try {
      const response = await fetch('http://localhost:5000/api/statements/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`
        },
        body: uploadFormData
      });

      const result = await response.json();
      
      if (response.ok) {
        onUploadSuccess(result.data);
        // Reset form
        setFile(null);
        setFormData({
          profileName: '',
          profileDescription: '',
          accountType: '',
          bankName: '',
          color: '#3B82F6',
          icon: 'wallet'
        });
      } else {
        alert(`Upload failed: ${result.error?.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>File:</label>
        <input 
          type="file" 
          onChange={(e) => setFile(e.target.files[0])} 
          required 
        />
      </div>
      
      <div>
        <label>Profile Name:</label>
        <input 
          type="text"
          value={formData.profileName}
          onChange={(e) => setFormData({...formData, profileName: e.target.value})}
          placeholder="e.g., Personal Account"
        />
      </div>
      
      <div>
        <label>Description:</label>
        <textarea
          value={formData.profileDescription}
          onChange={(e) => setFormData({...formData, profileDescription: e.target.value})}
          placeholder="Optional description"
        />
      </div>
      
      <div>
        <label>Account Type:</label>
        <select 
          value={formData.accountType}
          onChange={(e) => setFormData({...formData, accountType: e.target.value})}
        >
          <option value="">Select...</option>
          <option value="Checking">Checking</option>
          <option value="Savings">Savings</option>
          <option value="Credit Card">Credit Card</option>
          <option value="Business">Business</option>
        </select>
      </div>
      
      <div>
        <label>Bank Name:</label>
        <input 
          type="text"
          value={formData.bankName}
          onChange={(e) => setFormData({...formData, bankName: e.target.value})}
          placeholder="e.g., Ziraat Bankası"
        />
      </div>
      
      <div>
        <label>Color:</label>
        <input 
          type="color"
          value={formData.color}
          onChange={(e) => setFormData({...formData, color: e.target.value})}
        />
      </div>
      
      <div>
        <label>Icon:</label>
        <select 
          value={formData.icon}
          onChange={(e) => setFormData({...formData, icon: e.target.value})}
        >
          <option value="wallet">Wallet</option>
          <option value="credit-card">Credit Card</option>
          <option value="building">Building</option>
          <option value="bank">Bank</option>
        </select>
      </div>
      
      <button type="submit" disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload Statement'}
      </button>
    </form>
  );
}
```

---

### 3. Profile Management

**Update Profile Component:**
```javascript
function ProfileEditModal({ profile, onClose, onUpdate }) {
  const [formData, setFormData] = useState({
    profileName: profile.profileName || '',
    profileDescription: profile.profileDescription || '',
    accountType: profile.accountType || '',
    bankName: profile.bankName || '',
    color: profile.color || '#3B82F6',
    icon: profile.icon || 'wallet'
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const response = await fetch(
        `http://localhost:5000/api/statements/${profile.id}/profile`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(formData)
        }
      );

      const result = await response.json();
      if (response.ok) {
        onUpdate(result.data);
        onClose();
      } else {
        alert(`Update failed: ${result.error?.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Update error:', error);
      alert('Update failed. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal">
      {/* Form fields similar to upload form */}
      <button onClick={handleSave} disabled={saving}>
        {saving ? 'Saving...' : 'Save Changes'}
      </button>
      <button onClick={onClose}>Cancel</button>
    </div>
  );
}
```

**Set Default Profile:**
```javascript
async function setDefaultProfile(profileId) {
  try {
    const response = await fetch(
      `http://localhost:5000/api/statements/${profileId}/set-default`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      }
    );

    const result = await response.json();
    if (response.ok) {
      // Reload profiles to get updated isDefault values
      await loadProfiles();
      return result.data;
    } else {
      throw new Error(result.error?.message || 'Failed to set default profile');
    }
  } catch (error) {
    console.error('Set default error:', error);
    throw error;
  }
}
```

---

### 4. Filtering Analytics by Profile

**All analytics endpoints support `statementId` filtering:**

```javascript
// Category Breakdown
const response = await fetch(
  `http://localhost:5000/api/analytics/category-breakdown?statementId=${selectedProfileId}`,
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  }
);

// Spending Trends
const response = await fetch(
  `http://localhost:5000/api/analytics/spending-trends?statementId=${selectedProfileId}`,
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  }
);

// Financial Insights
const response = await fetch(
  `http://localhost:5000/api/analytics/insights?statementId=${selectedProfileId}`,
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  }
);
```

**Helper Function:**
```javascript
function buildAnalyticsUrl(endpoint, selectedProfileId, additionalParams = {}) {
  const baseUrl = `http://localhost:5000/api/analytics/${endpoint}`;
  const params = new URLSearchParams();
  
  if (selectedProfileId) {
    params.append('statementId', selectedProfileId);
  }
  
  Object.entries(additionalParams).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      params.append(key, value);
    }
  });
  
  return `${baseUrl}?${params.toString()}`;
}

// Usage
const url = buildAnalyticsUrl('category-breakdown', selectedProfileId, {
  startDate: '2024-01-01',
  endDate: '2024-01-31'
});
```

---

### 5. Profile Display Component

**Visual Profile Card:**
```javascript
function ProfileCard({ profile, isSelected, onSelect, onEdit, onSetDefault, onDelete }) {
  return (
    <div 
      className={`profile-card ${isSelected ? 'selected' : ''}`}
      style={{ borderLeftColor: profile.color || '#3B82F6' }}
      onClick={() => onSelect(profile)}
    >
      <div className="profile-header">
        <div className="profile-icon" style={{ color: profile.color }}>
          {getIcon(profile.icon)}
        </div>
        <div className="profile-info">
          <h3>{profile.profileName}</h3>
          {profile.accountType && (
            <span className="account-type">{profile.accountType}</span>
          )}
          {profile.bankName && (
            <span className="bank-name">{profile.bankName}</span>
          )}
        </div>
        {profile.isDefault && (
          <span className="default-badge">Default</span>
        )}
      </div>
      
      {profile.profileDescription && (
        <p className="profile-description">{profile.profileDescription}</p>
      )}
      
      <div className="profile-stats">
        <span>{profile.transactionCount} transactions</span>
        <span className={`status ${profile.status}`}>{profile.status}</span>
      </div>
      
      <div className="profile-actions">
        <button onClick={(e) => { e.stopPropagation(); onEdit(profile); }}>
          Edit
        </button>
        {!profile.isDefault && (
          <button onClick={(e) => { e.stopPropagation(); onSetDefault(profile.id); }}>
            Set Default
          </button>
        )}
        <button onClick={(e) => { e.stopPropagation(); onDelete(profile.id); }}>
          Delete
        </button>
      </div>
    </div>
  );
}
```

---

## State Management Recommendations

### Using React Context/State

```javascript
// ProfileContext.js
import { createContext, useContext, useState, useEffect } from 'react';

const ProfileContext = createContext();

export function ProfileProvider({ children }) {
  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfiles();
  }, []);

  async function loadProfiles() {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/statements/profiles', {
        headers: {
          'Authorization': `Bearer ${getAccessToken()}`
        }
      });
      const result = await response.json();
      const loadedProfiles = result.data.profiles;
      setProfiles(loadedProfiles);
      
      // Auto-select default or first profile
      const defaultProfile = loadedProfiles.find(p => p.isDefault);
      if (defaultProfile) {
        setSelectedProfile(defaultProfile);
      } else if (loadedProfiles.length > 0) {
        setSelectedProfile(loadedProfiles[0]);
      }
    } catch (error) {
      console.error('Failed to load profiles:', error);
    } finally {
      setLoading(false);
    }
  }

  async function refreshProfiles() {
    await loadProfiles();
  }

  return (
    <ProfileContext.Provider value={{
      profiles,
      selectedProfile,
      setSelectedProfile,
      refreshProfiles,
      loading
    }}>
      {children}
    </ProfileContext.Provider>
  );
}

export function useProfiles() {
  const context = useContext(ProfileContext);
  if (!context) {
    throw new Error('useProfiles must be used within ProfileProvider');
  }
  return context;
}
```

---

## Error Handling

**Common Error Responses:**
```javascript
// 404 - Statement/Profile not found
{
  "error": {
    "message": "Statement not found",
    "statusCode": 404,
    "errorCode": "STATEMENT_NOT_FOUND"
  }
}

// 403 - Access denied
{
  "error": {
    "message": "You do not have permission to access this statement",
    "statusCode": 403,
    "errorCode": "FORBIDDEN"
  }
}

// 400 - Invalid request
{
  "error": {
    "message": "No file provided",
    "statusCode": 400,
    "errorCode": "NO_FILE"
  }
}
```

**Error Handling Helper:**
```javascript
async function handleApiRequest(requestFn) {
  try {
    const response = await requestFn();
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.error?.message || 'Request failed');
    }
    
    return result.data;
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
}

// Usage
try {
  const profiles = await handleApiRequest(() => 
    fetch('http://localhost:5000/api/statements/profiles', {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    })
  );
} catch (error) {
  // Show error message to user
  showErrorNotification(error.message);
}
```

---

## Testing Checklist

- [ ] Run database migration script
- [ ] Upload file without profile metadata (should auto-generate profileName)
- [ ] Upload file with all profile metadata
- [ ] List profiles and verify sorting (default first)
- [ ] Select a profile and verify transactions are filtered
- [ ] Update profile metadata
- [ ] Set a profile as default (verify others become non-default)
- [ ] Delete a profile
- [ ] Verify analytics endpoints filter by selected profile
- [ ] Test with multiple profiles to ensure data separation

---

## Summary

The profile system allows users to:
1. **Organize** their financial data by account/profile
2. **Select** a profile to view filtered transactions and analytics
3. **Customize** profiles with names, colors, icons, and metadata
4. **Manage** profiles (update, set default, delete)

All existing endpoints (transactions, budgets, analytics) support `statementId` query parameter for filtering by selected profile.

**Key Integration Points:**
- Profile selection dropdown in navigation/header
- File upload form with profile metadata fields
- Profile management UI (edit, set default, delete)
- Filter all data requests by `selectedProfile.id` (as `statementId`)

