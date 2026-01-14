# Postman API Request Examples

Bu doküman, SpendWise API endpoint'lerini Postman'de test etmek için örnek request'leri içerir.

**Base URL:** `http://localhost:5000`

---

## 🔐 Authentication Endpoints

### 1. Register (Kullanıcı Kaydı)

**Method:** `POST`  
**URL:** `http://localhost:5000/api/auth/register`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "email": "test@example.com",
  "password": "Test123!@#",
  "name": "Test User"
}
```

**Alternatif Body (first_name/last_name ile):**
```json
{
  "email": "test@example.com",
  "password": "Test123!@#",
  "first_name": "Test",
  "last_name": "User",
  "username": "testuser"
}
```

**Expected Response (201):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "email": "test@example.com",
      "name": "Test User",
      "createdAt": "2024-01-15T10:30:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "User registered successfully"
}
```

---

### 2. Login (Giriş)

**Method:** `POST`  
**URL:** `http://localhost:5000/api/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "email": "test@example.com",
  "password": "Test123!@#"
}
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "email": "test@example.com",
      "name": "Test User"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Login successful"
}
```

**⚠️ Önemli:** Response'dan `access_token` değerini kopyalayın, diğer endpoint'ler için kullanacaksınız.

---

### 3. Get Current User (Mevcut Kullanıcı Bilgisi)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/auth/me`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "email": "test@example.com",
      "name": "Test User",
      "createdAt": "2024-01-15T10:30:00Z"
    }
  }
}
```

---

### 4. Update User Profile (Profil Güncelleme)

**Method:** `PUT`  
**URL:** `http://localhost:5000/api/auth/me`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "name": "Updated Name",
  "email": "newemail@example.com"
}
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "email": "newemail@example.com",
      "name": "Updated Name"
    }
  }
}
```

---

### 5. Change Password (Şifre Değiştirme)

**Method:** `POST`  
**URL:** `http://localhost:5000/api/auth/change-password`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "currentPassword": "Test123!@#",
  "newPassword": "NewPassword123!@#"
}
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Password changed successfully"
  }
}
```

---

### 6. Refresh Token (Token Yenileme)

**Method:** `POST`  
**URL:** `http://localhost:5000/api/auth/refresh`

**Headers:**
```
Authorization: Bearer YOUR_REFRESH_TOKEN_HERE
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "refresh_token": "YOUR_REFRESH_TOKEN_HERE"
}
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "NEW_ACCESS_TOKEN",
    "refresh_token": "NEW_REFRESH_TOKEN"
  },
  "message": "Token refreshed successfully"
}
```

---

### 7. Logout (Çıkış)

**Method:** `POST`  
**URL:** `http://localhost:5000/api/auth/logout`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  }
}
```

---

## 📄 Statement Endpoints

### 1. Upload Statement (Dosya Yükleme)

**Method:** `POST`  
**URL:** `http://localhost:5000/api/statements/upload`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Body (form-data):**
```
Key: file
Type: File
Value: [Select your PDF/Excel/CSV file]

Key: profileName (optional)
Type: Text
Value: Ana Hesap

Key: profileDescription (optional)
Type: Text
Value: Primary checking account

Key: accountType (optional)
Type: Text
Value: Checking

Key: bankName (optional)
Type: Text
Value: Garanti BBVA

Key: color (optional)
Type: Text
Value: #3B82F6

Key: icon (optional)
Type: Text
Value: account_balance
```

**Postman'de Nasıl Yapılır:**
1. Body sekmesine gidin
2. `form-data` seçeneğini seçin
3. `file` key'ini seçin, type'ı `File` yapın
4. Dosya seçin
5. Diğer profil alanlarını ekleyin (opsiyonel)

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "stmt_123",
    "fileName": "statement.pdf",
    "uploadDate": "2024-01-15T10:30:00Z",
    "status": "processing",
    "transactionCount": 0,
    "profileName": "Ana Hesap",
    "profileDescription": "Primary checking account",
    "accountType": "Checking",
    "bankName": "Garanti BBVA",
    "color": "#3B82F6",
    "icon": "account_balance",
    "isDefault": true
  },
  "message": "Statement uploaded successfully"
}
```

**Not:** İlk yüklenen statement otomatik olarak `isDefault: true` olur.

---

### 2. List Statements (Statement Listesi)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/statements`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "statements": [
      {
        "id": "stmt_123",
        "fileName": "statement.pdf",
        "uploadDate": "2024-01-15T10:30:00Z",
        "status": "processed",
        "transactionCount": 50,
        "statementPeriodStart": "2024-01-01T00:00:00Z",
        "statementPeriodEnd": "2024-01-31T23:59:59Z",
        "isProcessed": true,
        "profileName": "Ana Hesap",
        "isDefault": true
      }
    ]
  }
}
```

---

### 3. Get Statement Details (Statement Detayı)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/statements/{statement_id}`

**Örnek:** `http://localhost:5000/api/statements/stmt_123`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "stmt_123",
    "fileName": "statement.pdf",
    "uploadDate": "2024-01-15T10:30:00Z",
    "status": "processed",
    "transactionCount": 50,
    "profileName": "Ana Hesap",
    "profileDescription": "Primary checking account",
    "accountType": "Checking",
    "bankName": "Garanti BBVA",
    "color": "#3B82F6",
    "icon": "account_balance",
    "isDefault": true
  }
}
```

---

### 4. List Profiles (Profil Listesi)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/statements/profiles`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "profiles": [
      {
        "id": "stmt_123",
        "profileName": "Ana Hesap",
        "accountType": "Checking",
        "bankName": "Garanti BBVA",
        "color": "#3B82F6",
        "icon": "account_balance",
        "isDefault": true,
        "transactionCount": 50,
        "status": "processed"
      }
    ]
  }
}
```

---

### 5. Update Profile (Profil Güncelleme)

**Method:** `PUT`  
**URL:** `http://localhost:5000/api/statements/{statement_id}/profile`

**Örnek:** `http://localhost:5000/api/statements/stmt_123/profile`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "profileName": "Updated Profile Name",
  "profileDescription": "Updated description",
  "accountType": "Savings",
  "bankName": "Yapı Kredi",
  "color": "#10B981",
  "icon": "savings"
}
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "stmt_123",
    "profileName": "Updated Profile Name",
    "profileDescription": "Updated description",
    "accountType": "Savings",
    "bankName": "Yapı Kredi",
    "color": "#10B981",
    "icon": "savings"
  }
}
```

---

### 6. Set Default Profile (Varsayılan Profil Ayarlama)

**Method:** `POST`  
**URL:** `http://localhost:5000/api/statements/{statement_id}/set-default`

**Örnek:** `http://localhost:5000/api/statements/stmt_123/set-default`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Default statement updated"
  }
}
```

---

### 7. Delete Statement (Statement Silme)

**Method:** `POST`  
**URL:** `http://localhost:5000/api/statements/{statement_id}/delete`

**Örnek:** `http://localhost:5000/api/statements/stmt_123/delete`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Statement deleted successfully"
  }
}
```

---

## 💰 Transaction Endpoints

### 1. Get Transactions (Transaction Listesi)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/transactions`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Query Parameters (Tümü Opsiyonel):**
```
statementId=stmt_123
startDate=2024-01-01T00:00:00Z
endDate=2024-01-31T23:59:59Z
category=Gıda
account=Ana Hesap
limit=50
offset=0
```

**Örnek URL'ler:**

**Tüm transaction'lar:**
```
http://localhost:5000/api/transactions
```

**Belirli bir profil için:**
```
http://localhost:5000/api/transactions?statementId=stmt_123
```

**Tarih aralığı ile:**
```
http://localhost:5000/api/transactions?startDate=2024-01-01T00:00:00Z&endDate=2024-01-31T23:59:59Z
```

**Kategori filtresi ile:**
```
http://localhost:5000/api/transactions?category=Gıda
```

**Profil + Tarih + Kategori:**
```
http://localhost:5000/api/transactions?statementId=stmt_123&startDate=2024-01-01T00:00:00Z&endDate=2024-01-31T23:59:59Z&category=Gıda&limit=20&offset=0
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": "txn_123",
        "date": "2024-01-15T10:30:00Z",
        "description": "Migros Market alışverişi",
        "amount": 245.50,
        "type": "expense",
        "category": "Gıda",
        "merchant": "Migros",
        "account": "Ana Hesap",
        "referenceNumber": "REF123456",
        "statementId": "stmt_123"
      },
      {
        "id": "txn_124",
        "date": "2024-01-14T09:00:00Z",
        "description": "Maaş ödemesi",
        "amount": 20000.00,
        "type": "income",
        "category": null,
        "account": "Ana Hesap",
        "statementId": "stmt_123"
      }
    ],
    "total": 100,
    "limit": 50,
    "offset": 0
  }
}
```

---

### 2. Get Transaction Summary (Transaction Özeti)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/transactions/summary`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Query Parameters (Tümü Opsiyonel):**
```
statementId=stmt_123
startDate=2024-01-01T00:00:00Z
endDate=2024-01-31T23:59:59Z
```

**Örnek URL:**
```
http://localhost:5000/api/transactions/summary?statementId=stmt_123&startDate=2024-01-01T00:00:00Z&endDate=2024-01-31T23:59:59Z
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "totalIncome": 20000.00,
    "totalExpenses": 15000.00,
    "savings": 5000.00,
    "transactionCount": 50,
    "period": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-31T23:59:59Z"
    }
  }
}
```

---

## 📊 Budget Endpoints

### 1. Create/Update Budget (Bütçe Oluşturma/Güncelleme)

**Method:** `POST`  
**URL:** `http://localhost:5000/api/budgets`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "categoryId": "food",
  "categoryName": "Gıda",
  "amount": 2500.00,
  "period": "monthly",
  "startDate": "2024-01-01T00:00:00Z"
}
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "budget_123",
    "categoryId": "food",
    "categoryName": "Gıda",
    "amount": 2500.00,
    "period": "monthly",
    "startDate": "2024-01-01T00:00:00Z",
    "endDate": "2024-01-31T23:59:59Z",
    "createdAt": "2024-01-01T00:00:00Z"
  },
  "message": "Budget saved successfully"
}
```

---

### 2. List Budgets (Bütçe Listesi)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/budgets`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Query Parameters (Opsiyonel):**
```
period=monthly
categoryId=food
```

**Örnek URL:**
```
http://localhost:5000/api/budgets?period=monthly
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "budgets": [
      {
        "id": "budget_123",
        "categoryId": "food",
        "categoryName": "Gıda",
        "amount": 2500.00,
        "period": "monthly",
        "startDate": "2024-01-01T00:00:00Z",
        "endDate": "2024-01-31T23:59:59Z"
      }
    ]
  }
}
```

---

### 3. Compare Budgets (Bütçe Karşılaştırması)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/budgets/compare`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Query Parameters (Opsiyonel):**
```
statementId=stmt_123
```

**Örnek URL:**
```
http://localhost:5000/api/budgets/compare?statementId=stmt_123
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "comparisons": [
      {
        "budget": {
          "id": "budget_123",
          "categoryId": "food",
          "categoryName": "Gıda",
          "amount": 2500.00
        },
        "actualSpending": 2450.50,
        "remaining": 49.50,
        "percentageUsed": 98.02,
        "isOverBudget": false,
        "status": "on_track"
      }
    ]
  }
}
```

---

### 4. Delete Budget (Bütçe Silme)

**Method:** `DELETE`  
**URL:** `http://localhost:5000/api/budgets/{budget_id}`

**Örnek:** `http://localhost:5000/api/budgets/budget_123`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Budget deleted successfully"
  }
}
```

---

## 📈 Analytics Endpoints

Tüm analytics endpoint'leri `statementId` query parametresi ile profil filtresi destekler.

### 1. Get Category Breakdown (Kategori Dağılımı)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/analytics/categories`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Query Parameters (Opsiyonel):**
```
statementId=stmt_123
startDate=2024-01-01T00:00:00Z
endDate=2024-01-31T23:59:59Z
```

**Örnek URL:**
```
http://localhost:5000/api/analytics/categories?statementId=stmt_123
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "category": "Gıda",
      "totalAmount": 2450.50,
      "percentage": 28.8,
      "transactionCount": 15
    },
    {
      "category": "Ulaşım",
      "totalAmount": 1150.50,
      "percentage": 13.5,
      "transactionCount": 8
    }
  ]
}
```

---

### 2. Get Spending Trends (Harcama Trendleri)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/analytics/trends`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Query Parameters (Opsiyonel):**
```
statementId=stmt_123
startDate=2024-01-01T00:00:00Z
endDate=2024-01-31T23:59:59Z
period=day
```

**Period Değerleri:** `day`, `week`, `month`

**Örnek URL:**
```
http://localhost:5000/api/analytics/trends?statementId=stmt_123&period=day
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-01-15T00:00:00Z",
      "income": 500.00,
      "expenses": 300.00,
      "savings": 200.00
    },
    {
      "date": "2024-01-16T00:00:00Z",
      "income": 0.00,
      "expenses": 150.00,
      "savings": -150.00
    }
  ]
}
```

---

### 3. Get Financial Insights (Finansal Öngörüler)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/analytics/insights`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Query Parameters (Opsiyonel):**
```
statementId=stmt_123
```

**Örnek URL:**
```
http://localhost:5000/api/analytics/insights?statementId=stmt_123
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "savingsRate": 20.5,
    "topSpendingCategory": "Gıda",
    "averageDailySpending": 100.00,
    "biggestExpense": 500.00,
    "recommendations": [
      "Your spending on Gıda is 35% higher than average",
      "Consider setting a budget for Ulaşım category"
    ]
  }
}
```

---

### 4. Get Monthly Trends (Aylık Trendler)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/analytics/monthly-trends`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Query Parameters (Opsiyonel):**
```
statementId=stmt_123
```

**Örnek URL:**
```
http://localhost:5000/api/analytics/monthly-trends?statementId=stmt_123
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "month": "2024-01-01T00:00:00Z",
      "income": 20000.00,
      "expenses": 15000.00,
      "savings": 5000.00
    },
    {
      "month": "2024-02-01T00:00:00Z",
      "income": 20000.00,
      "expenses": 14000.00,
      "savings": 6000.00
    }
  ]
}
```

---

### 5. Get Category Trends (Kategori Trendleri)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/analytics/category-trends`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Query Parameters (Opsiyonel):**
```
statementId=stmt_123
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "category": "Gıda",
      "color": "#FF5733",
      "monthlyData": [
        {
          "month": "2024-01-01T00:00:00Z",
          "amount": 2450.50
        },
        {
          "month": "2024-02-01T00:00:00Z",
          "amount": 2600.00
        }
      ]
    }
  ]
}
```

---

### 6. Get Weekly Patterns (Haftalık Pattern'ler)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/analytics/weekly-patterns`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Query Parameters (Opsiyonel):**
```
statementId=stmt_123
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "dayOfWeek": 1,
      "averageSpending": 120.50,
      "transactionCount": 15
    },
    {
      "dayOfWeek": 2,
      "averageSpending": 95.30,
      "transactionCount": 12
    }
  ]
}
```

**Not:** `dayOfWeek` 1-7 arası (1 = Pazartesi, 7 = Pazar)

---

### 7. Get Year-over-Year (Yıl Bazında Karşılaştırma)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/analytics/year-over-year`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Query Parameters (Opsiyonel):**
```
statementId=stmt_123
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "month": "2024-01-01T00:00:00Z",
      "currentYear": 15000.00,
      "previousYear": 14000.00,
      "changePercent": 7.14
    }
  ]
}
```

---

### 8. Get Forecast (Harcama Tahmini)

**Method:** `GET`  
**URL:** `http://localhost:5000/api/analytics/forecast`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Query Parameters (Opsiyonel):**
```
statementId=stmt_123
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "predictedExpenses": 15000.00,
    "predictedIncome": 20000.00,
    "predictedSavings": 5000.00,
    "confidence": 85.5,
    "basedOnMonths": 6
  }
}
```

---

## 🔧 Postman Collection Setup

### Environment Variables (Ortam Değişkenleri)

Postman'de Environment oluşturun ve şu değişkenleri ekleyin:

```
base_url: http://localhost:5000
access_token: (Login sonrası otomatik doldurulacak)
refresh_token: (Login sonrası otomatik doldurulacak)
statement_id: (Upload sonrası otomatik doldurulacak)
```

### Pre-request Script (Login için)

Login request'ine Pre-request Script ekleyin:

```javascript
// Environment variables'ı temizle
pm.environment.unset("access_token");
pm.environment.unset("refresh_token");
```

### Tests Script (Login için)

Login request'ine Tests Script ekleyin:

```javascript
// Response'u parse et
var jsonData = pm.response.json();

// Token'ları environment'a kaydet
if (jsonData.success && jsonData.data.access_token) {
    pm.environment.set("access_token", jsonData.data.access_token);
    pm.environment.set("refresh_token", jsonData.data.refresh_token);
    console.log("Tokens saved to environment");
}
```

### Tests Script (Upload için)

Upload request'ine Tests Script ekleyin:

```javascript
// Response'u parse et
var jsonData = pm.response.json();

// Statement ID'yi environment'a kaydet
if (jsonData.success && jsonData.data.id) {
    pm.environment.set("statement_id", jsonData.data.id);
    console.log("Statement ID saved: " + jsonData.data.id);
}
```

### Authorization Header (Tüm Protected Endpoint'ler için)

Authorization header'ında environment variable kullanın:

```
Authorization: Bearer {{access_token}}
```

---

## 🚨 Hata Response Örnekleri

### 401 Unauthorized (Token Yok/Geçersiz)

```json
{
  "success": false,
  "error": {
    "message": "Authorization token is missing",
    "code": "MISSING_TOKEN",
    "statusCode": 401
  }
}
```

### 400 Bad Request (Geçersiz İstek)

```json
{
  "success": false,
  "error": {
    "message": "Email and password are required",
    "code": "MISSING_CREDENTIALS",
    "statusCode": 400
  }
}
```

### 404 Not Found (Kaynak Bulunamadı)

```json
{
  "success": false,
  "error": {
    "message": "Statement not found",
    "code": "STATEMENT_NOT_FOUND",
    "statusCode": 404
  }
}
```

### 403 Forbidden (Erişim Reddedildi)

```json
{
  "success": false,
  "error": {
    "message": "Access denied",
    "code": "FORBIDDEN",
    "statusCode": 403
  }
}
```

---

## 📝 Önemli Notlar

1. **Token Kullanımı:**
   - `access_token` 15 dakika geçerlidir
   - Süresi dolduğunda `refresh_token` ile yenileyin
   - Tüm protected endpoint'lerde `Authorization: Bearer {token}` header'ı gerekli

2. **Tarih Formatı:**
   - Tüm tarihler ISO 8601 formatında olmalı: `2024-01-15T10:30:00Z`
   - `Z` UTC timezone'u belirtir

3. **Profil Filtreleme:**
   - `statementId` parametresi ile belirli bir profil için filtreleme yapılır
   - Parametre yoksa tüm profillerden veri gelir

4. **Pagination:**
   - Transaction listesinde `limit` (max 100) ve `offset` kullanılır
   - Varsayılan: `limit=50`, `offset=0`

5. **File Upload:**
   - Desteklenen formatlar: PDF, XLSX, XLS, CSV
   - Max dosya boyutu: 10MB
   - `multipart/form-data` formatında gönderilir

---

## 🎯 Hızlı Test Senaryosu

1. **Register/Login:**
   ```
   POST /api/auth/register
   → access_token al
   ```

2. **Upload Statement:**
   ```
   POST /api/statements/upload
   → statement_id al
   ```

3. **Get Transactions:**
   ```
   GET /api/transactions?statementId={statement_id}
   ```

4. **Get Analytics:**
   ```
   GET /api/analytics/categories?statementId={statement_id}
   ```

5. **Create Budget:**
   ```
   POST /api/budgets
   ```

6. **Compare Budget:**
   ```
   GET /api/budgets/compare?statementId={statement_id}
   ```

---

**Hazır!** Artık Postman'de tüm endpoint'leri test edebilirsiniz. 🚀
