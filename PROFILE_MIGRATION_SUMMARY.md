# Profile System Migration - Quick Summary

## Database Migration

**Run this command once:**
```bash
python migrate_add_profile_fields.py
```

**What it does:**
- Adds 7 new columns to `statements` table
- Updates existing records with default `profile_name = file_name`
- Safe to run multiple times (checks if columns exist)

---

## New API Endpoints

### 1. Upload with Profile Metadata
```
POST /api/statements/upload
Content-Type: multipart/form-data

Fields:
- file (required)
- profileName (optional)
- profileDescription (optional)
- accountType (optional)
- bankName (optional)
- color (optional) - Hex color code
- icon (optional) - Icon identifier
```

### 2. List Profiles (Simplified)
```
GET /api/statements/profiles
Returns: Simplified profile list for dropdowns
```

### 3. Update Profile
```
PUT /api/statements/{id}/profile
Content-Type: application/json

Body: { profileName, profileDescription, accountType, bankName, color, icon }
```

### 4. Set Default Profile
```
POST /api/statements/{id}/set-default
Sets this profile as default, unsets all others
```

---

## Updated Endpoints

### List Statements
- Now includes profile metadata in response
- Sorted by `isDefault DESC, uploadDate DESC`

### Get Statement
- Now includes profile metadata in response

---

## Frontend Integration Points

1. **Profile Selection Dropdown**
   - Use `GET /api/statements/profiles` to populate
   - Store selected profile ID in state/context
   - Pass `statementId={selectedProfileId}` to all data requests

2. **File Upload Form**
   - Add profile metadata fields (all optional)
   - Auto-generates `profileName` from filename if not provided

3. **Profile Management**
   - Edit profile: `PUT /api/statements/{id}/profile`
   - Set default: `POST /api/statements/{id}/set-default`
   - Delete: `POST /api/statements/{id}/delete` (existing)

4. **Data Filtering**
   - All endpoints support `statementId` query parameter
   - Transactions: `GET /api/transactions?statementId={id}`
   - Analytics: `GET /api/analytics/{endpoint}?statementId={id}`
   - Budgets: `GET /api/budgets?statementId={id}`

---

## Response Format Changes

All statement responses now include:
```json
{
  "profileName": "Personal Account",
  "profileDescription": "My main account",
  "accountType": "Checking",
  "bankName": "Ziraat Bankası",
  "color": "#3B82F6",
  "icon": "wallet",
  "isDefault": true
}
```

---

## Business Logic

1. **First Profile = Default**
   - First uploaded profile automatically gets `isDefault=true`

2. **Auto-Generated Profile Name**
   - If `profileName` not provided, uses filename (without extension)

3. **One Default at a Time**
   - Setting a profile as default unsets all others

4. **Profile Selection**
   - When profile selected, filter all data by `statementId`
   - If no profile selected, show all data (existing behavior)

---

## Testing Steps

1. Run migration: `python migrate_add_profile_fields.py`
2. Upload file with profile metadata
3. List profiles and verify default profile
4. Select profile and verify transactions are filtered
5. Update profile metadata
6. Set different profile as default
7. Verify analytics filter by selected profile

---

## Full Documentation

See `PROFILE_SYSTEM_FRONTEND_GUIDE.md` for:
- Complete API documentation
- JavaScript code examples
- React component examples
- State management patterns
- Error handling

