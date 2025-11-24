"""
Fake Statement Analyzer
A modular fake analyzer that generates mock transactions for MVP purposes.
Designed to be easily replaceable with a real AI/ML analyzer later.
"""
import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

from models.transaction import Transaction


@dataclass
class AnalysisResult:
    """Result of statement analysis"""
    transactions: List[Transaction]
    statement_period_start: datetime
    statement_period_end: datetime
    metadata: Dict[str, Any]


class StatementAnalyzer:
    """
    Abstract base class for statement analyzers.
    This interface allows easy swapping of fake analyzer with real AI/ML analyzer.
    """
    
    def analyze(self, file_path: str, user_id: str, statement_id: str) -> AnalysisResult:
        """
        Analyzes a statement file and extracts transactions.
        
        Args:
            file_path: Path to the statement file
            user_id: ID of the user who uploaded the statement
            statement_id: ID of the statement record
            
        Returns:
            AnalysisResult with transactions, period dates, and metadata
        """
        raise NotImplementedError("Subclasses must implement analyze method")


class FakeStatementAnalyzer(StatementAnalyzer):
    """
    Fake analyzer that generates mock transactions.
    Uses statement_id as seed for consistency - same statement always generates same transactions.
    Generates realistic financial data with income-based expense budgeting.
    """
    
    # Turkish minimum wage baseline (2024)
    MIN_INCOME = 17000  # TRY/month
    MAX_INCOME = 25000  # TRY/month
    
    # Expense ratio: 75-90% of income
    MIN_EXPENSE_RATIO = 0.75
    MAX_EXPENSE_RATIO = 0.90
    
    # Category budget allocation (as percentage of total expenses)
    # Based on Turkish household spending patterns
    CATEGORY_BUDGET_PERCENTAGES = {
        'Gıda': (0.25, 0.30),        # 25-30% of expenses
        'Ulaşım': (0.15, 0.20),      # 15-20% of expenses
        'Faturalar': (0.15, 0.20),   # 15-20% of expenses (rent, utilities, bills)
        'Alışveriş': (0.10, 0.15),   # 10-15% of expenses
        'Eğlence': (0.05, 0.10),     # 5-10% of expenses
        'Sağlık': (0.05, 0.08),      # 5-8% of expenses
        'Eğitim': (0.03, 0.05),      # 3-5% of expenses
        'Diğer': (0.05, 0.10)        # 5-10% of expenses
    }
    
    # Turkish categories with realistic amount ranges and merchants
    CATEGORIES = {
        'Gıda': {
            'merchants': ['Migros Market Alışverişi', 'Getir Yemek', 'CarrefourSA', 'Bim Market', 'Şok Market', 'A101', 'Yemeksepeti'],
            'daily_frequency': (1, 3),  # 1-3 transactions per day
            'base_amount_range': (50, 300)  # Base range, will be scaled by income
        },
        'Ulaşım': {
            'merchants': ['IstanbulKart Yükleme', 'Uber Yolculuk', 'Benzin İstasyonu', 'Metro İstanbul', 'Otobüs Bileti', 'Taksi'],
            'daily_frequency': (0.5, 1.5),  # 0.5-1.5 transactions per day
            'base_amount_range': (30, 200)
        },
        'Alışveriş': {
            'merchants': ['Amazon.com.tr', 'H&M Mağaza', 'Teknosa', 'MediaMarkt', 'Trendyol', 'Hepsiburada', 'LC Waikiki'],
            'weekly_frequency': (1, 2),  # 1-2 per week
            'base_amount_range': (200, 2000)
        },
        'Faturalar': {
            'fixed_expenses': {
                'Kira': (2000, 5000),  # Rent: 2,000-5,000 TRY
                'Elektrik Faturası': (200, 500),
                'Su Faturası': (100, 300),
                'Doğalgaz Faturası': (300, 800),
                'İnternet Faturası': (150, 300),
                'Telefon Faturası': (100, 250)
            },
            'merchants': ['Elektrik Faturası', 'Su Faturası', 'İnternet Faturası', 'Telefon Faturası', 'Doğalgaz Faturası', 'Kira'],
            'base_amount_range': (100, 500)  # For non-fixed bills
        },
        'Eğlence': {
            'merchants': ['Sinema Bileti', 'Netflix Abonelik', 'Spotify Premium', 'Kafe', 'Restoran', 'Konser Bileti', 'Tiyatro'],
            'weekly_frequency': (1, 3),  # 1-3 per week, more on weekends
            'base_amount_range': (100, 500)
        },
        'Sağlık': {
            'merchants': ['Eczane', 'Hastane', 'Doktor Muayenesi', 'Sağlık Sigortası', 'Diş Hekimi'],
            'monthly_frequency': (1, 2),  # 1-2 per month
            'base_amount_range': (150, 600)
        },
        'Eğitim': {
            'merchants': ['Kitap Satın Alma', 'Online Kurs', 'Eğitim Materyali', 'Dershane', 'Yabancı Dil Kursu'],
            'monthly_frequency': (0.5, 1.5),  # 0.5-1.5 per month
            'base_amount_range': (200, 450)
        },
        'Diğer': {
            'merchants': ['Diğer Harcama', 'Nakit Çekme', 'ATM İşlemi', 'Banka Komisyonu', 'Havale'],
            'weekly_frequency': (0.5, 1.5),
            'base_amount_range': (100, 500)
        }
    }
    
    INCOME_SOURCES = {
        'primary': ['Maaş Ödemesi', 'Aylık Maaş', 'Maaş Transferi'],
        'secondary': ['Freelance Ödeme', 'Proje Ödemesi', 'Yan İş Geliri'],
        'bonus': ['Bonus Ödemesi', 'Prim Ödemesi', 'Yıllık İkramiye']
    }
    
    def __init__(self):
        """Initialize the fake analyzer"""
        pass
    
    def analyze(self, file_path: str, user_id: str, statement_id: str) -> AnalysisResult:
        """
        Generate realistic mock transactions for a statement.
        
        Algorithm:
        1. Generate all income transactions first
        2. Calculate total income and target expense budget (75-90% of income)
        3. Allocate budget to categories based on percentages
        4. Generate expense transactions until category budgets are met
        
        Uses statement_id as seed to ensure consistency - same statement always
        generates the same transactions.
        """
        # Use statement_id as seed for consistency
        seed = self._generate_seed(statement_id)
        random.seed(seed)
        
        # Generate date range (last 30 days from now)
        upload_date = datetime.utcnow()
        statement_period_end = upload_date.replace(hour=23, minute=59, second=59, microsecond=0)
        statement_period_start = (statement_period_end - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        transactions = []
        
        # Step 1: Generate income transactions
        income_transactions = self._generate_income_transactions(
            user_id, statement_id, statement_period_start, statement_period_end
        )
        transactions.extend(income_transactions)
        
        # Step 2: Calculate total income and target expense budget
        total_income = sum(txn.amount for txn in income_transactions)
        expense_ratio = random.uniform(self.MIN_EXPENSE_RATIO, self.MAX_EXPENSE_RATIO)
        target_expense_budget = total_income * expense_ratio
        
        # Step 3: Allocate budget to categories
        category_budgets = self._allocate_category_budgets(target_expense_budget)
        
        # Step 4: Generate expense transactions
        expense_transactions = self._generate_expense_transactions(
            user_id, statement_id, statement_period_start, statement_period_end,
            category_budgets, total_income
        )
        transactions.extend(expense_transactions)
        
        # Sort transactions by date
        transactions.sort(key=lambda x: x.date)
        
        # Reset random seed
        random.seed()
        
        return AnalysisResult(
            transactions=transactions,
            statement_period_start=statement_period_start,
            statement_period_end=statement_period_end,
            metadata={
                'analyzer': 'fake',
                'version': '2.0.0',
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'total_income': total_income,
                'total_expenses': sum(txn.amount for txn in expense_transactions),
                'expense_ratio': expense_ratio
            }
        )
    
    def _generate_income_transactions(
        self, user_id: str, statement_id: str,
        period_start: datetime, period_end: datetime
    ) -> List[Transaction]:
        """Generate income transactions (salary + optional additional income)"""
        income_transactions = []
        
        # Primary salary: Always generate on 1st-5th of month within period
        # Find the first day of the month that falls within the period
        salary_date = None
        
        # Try current month's 1st-5th
        for day in range(1, 6):
            try:
                candidate_date = period_start.replace(day=day, hour=9, minute=0)
                if period_start <= candidate_date <= period_end:
                    salary_date = candidate_date
                    break
            except ValueError:
                continue
        
        # If not found, try next month's 1st-5th
        if salary_date is None:
            if period_start.month == 12:
                next_month = period_start.replace(year=period_start.year + 1, month=1, day=1)
            else:
                next_month = period_start.replace(month=period_start.month + 1, day=1)
            
            for day in range(1, 6):
                try:
                    candidate_date = next_month.replace(day=day, hour=9, minute=0)
                    if period_start <= candidate_date <= period_end:
                        salary_date = candidate_date
                        break
                except ValueError:
                    continue
        
        # If still not found, use a date within the first week of period
        if salary_date is None:
            days_offset = random.randint(0, min(6, (period_end - period_start).days))
            salary_date = period_start + timedelta(days=days_offset)
            salary_date = salary_date.replace(hour=9, minute=0)
        
        # Generate salary transaction
        if salary_date and period_start <= salary_date <= period_end:
            salary_amount = random.uniform(self.MIN_INCOME, self.MAX_INCOME)
            salary_txn = Transaction(
                user_id=user_id,
                statement_id=statement_id,
                date=salary_date,
                description=random.choice(self.INCOME_SOURCES['primary']),
                amount=salary_amount,
                type='income',
                category=None,
                merchant=None,
                account='Ana Hesap',
                reference_number=f'SAL{random.randint(100000, 999999)}'
            )
            income_transactions.append(salary_txn)
        
        # Secondary income: Freelance (20% chance)
        if random.random() < 0.20:
            freelance_date = period_start + timedelta(days=random.randint(10, 25))
            if freelance_date <= period_end:
                freelance_amount = random.uniform(2000, 5000)
                freelance_txn = Transaction(
                    user_id=user_id,
                    statement_id=statement_id,
                    date=freelance_date,
                    description=random.choice(self.INCOME_SOURCES['secondary']),
                    amount=freelance_amount,
                    type='income',
                    category=None,
                    merchant=None,
                    account='Ana Hesap',
                    reference_number=f'FRE{random.randint(100000, 999999)}'
                )
                income_transactions.append(freelance_txn)
        
        # Bonus income: (10% chance)
        if random.random() < 0.10:
            bonus_date = period_start + timedelta(days=random.randint(5, 15))
            if bonus_date <= period_end:
                bonus_amount = random.uniform(1000, 3000)
                bonus_txn = Transaction(
                    user_id=user_id,
                    statement_id=statement_id,
                    date=bonus_date,
                    description=random.choice(self.INCOME_SOURCES['bonus']),
                    amount=bonus_amount,
                    type='income',
                    category=None,
                    merchant=None,
                    account='Ana Hesap',
                    reference_number=f'BNS{random.randint(100000, 999999)}'
                )
                income_transactions.append(bonus_txn)
        
        return income_transactions
    
    def _allocate_category_budgets(self, total_budget: float) -> Dict[str, float]:
        """Allocate total expense budget to categories based on percentages"""
        category_budgets = {}
        remaining_budget = total_budget
        
        # Allocate budgets for each category
        categories = list(self.CATEGORY_BUDGET_PERCENTAGES.keys())
        random.shuffle(categories)  # Randomize order for variety
        
        for i, category in enumerate(categories):
            min_pct, max_pct = self.CATEGORY_BUDGET_PERCENTAGES[category]
            
            if i == len(categories) - 1:
                # Last category gets remaining budget
                category_budgets[category] = remaining_budget
            else:
                # Allocate based on percentage range
                pct = random.uniform(min_pct, max_pct)
                allocated = total_budget * pct
                category_budgets[category] = allocated
                remaining_budget -= allocated
        
        return category_budgets
    
    def _generate_expense_transactions(
        self, user_id: str, statement_id: str,
        period_start: datetime, period_end: datetime,
        category_budgets: Dict[str, float], total_income: float
    ) -> List[Transaction]:
        """Generate expense transactions based on category budgets"""
        transactions = []
        days_in_period = (period_end - period_start).days + 1
        
        # First, generate fixed expenses (rent, utilities) for Faturalar category
        faturalar_budget = category_budgets.get('Faturalar', 0)
        fixed_expenses = self._generate_fixed_expenses(
            user_id, statement_id, period_start, period_end, faturalar_budget
        )
        transactions.extend(fixed_expenses)
        
        # Track remaining budget for Faturalar (after fixed expenses)
        fixed_expenses_total = sum(txn.amount for txn in fixed_expenses)
        remaining_faturalar_budget = max(0, faturalar_budget - fixed_expenses_total)
        category_budgets['Faturalar'] = remaining_faturalar_budget
        
        # Generate variable expenses for each category
        for category, budget in category_budgets.items():
            if budget <= 0:
                continue
            
            category_transactions = self._generate_category_transactions(
                user_id, statement_id, category, budget,
                period_start, period_end, days_in_period, total_income
            )
            transactions.extend(category_transactions)
        
        return transactions
    
    def _generate_fixed_expenses(
        self, user_id: str, statement_id: str,
        period_start: datetime, period_end: datetime,
        total_budget: float
    ) -> List[Transaction]:
        """Generate fixed monthly expenses (rent, utilities)"""
        transactions = []
        fixed_expenses_config = self.CATEGORIES['Faturalar']['fixed_expenses']
        
        # Always generate rent (largest fixed expense)
        rent_amount = random.uniform(*fixed_expenses_config['Kira'])
        rent_date = period_start.replace(day=random.randint(1, 5), hour=10, minute=0)
        if rent_date < period_start:
            rent_date = period_start.replace(day=1, hour=10, minute=0)
        
        if rent_date <= period_end:
            rent_txn = Transaction(
                user_id=user_id,
                statement_id=statement_id,
                date=rent_date,
                description='Kira Ödemesi',
                amount=rent_amount,
                type='expense',
                category='Faturalar',
                merchant='Kira',
                account='Ana Hesap',
                reference_number=f'RENT{random.randint(100000, 999999)}'
            )
            transactions.append(rent_txn)
        
        # Generate utilities (electricity, water, gas, internet, phone)
        utilities = ['Elektrik Faturası', 'Su Faturası', 'Doğalgaz Faturası', 'İnternet Faturası', 'Telefon Faturası']
        remaining_budget = total_budget - rent_amount
        
        for utility in utilities:
            if utility in fixed_expenses_config and remaining_budget > 0:
                utility_amount = random.uniform(*fixed_expenses_config[utility])
                if utility_amount <= remaining_budget:
                    utility_date = period_start.replace(day=random.randint(1, 10), hour=14, minute=0)
                    if utility_date < period_start:
                        utility_date = period_start.replace(day=1, hour=14, minute=0)
                    
                    if utility_date <= period_end:
                        utility_txn = Transaction(
                            user_id=user_id,
                            statement_id=statement_id,
                            date=utility_date,
                            description=f'{utility} - {utility_date.strftime("%B %Y")}',
                            amount=utility_amount,
                            type='expense',
                            category='Faturalar',
                            merchant=utility,
                            account='Ana Hesap',
                            reference_number=f'UTIL{random.randint(100000, 999999)}'
                        )
                        transactions.append(utility_txn)
                        remaining_budget -= utility_amount
        
        return transactions
    
    def _generate_category_transactions(
        self, user_id: str, statement_id: str, category: str, budget: float,
        period_start: datetime, period_end: datetime, days_in_period: int,
        total_income: float
    ) -> List[Transaction]:
        """Generate transactions for a specific category within budget"""
        transactions = []
        category_info = self.CATEGORIES[category]
        spent = 0.0
        max_iterations = 200  # Prevent infinite loops
        iteration = 0
        
        # Scale amount ranges based on income level
        income_factor = total_income / self.MIN_INCOME
        base_min, base_max = category_info['base_amount_range']
        min_amount = base_min * (0.8 + 0.4 * income_factor)  # Scale between 0.8x and 1.2x
        max_amount = base_max * (0.8 + 0.4 * income_factor)
        
        # Determine transaction frequency
        if 'daily_frequency' in category_info:
            min_freq, max_freq = category_info['daily_frequency']
            num_transactions = int(days_in_period * random.uniform(min_freq, max_freq))
        elif 'weekly_frequency' in category_info:
            min_freq, max_freq = category_info['weekly_frequency']
            num_transactions = int((days_in_period / 7) * random.uniform(min_freq, max_freq))
        elif 'monthly_frequency' in category_info:
            min_freq, max_freq = category_info['monthly_frequency']
            num_transactions = int(random.uniform(min_freq, max_freq))
        else:
            num_transactions = random.randint(5, 15)
        
        # Generate transactions
        while spent < budget * 0.95 and iteration < max_iterations and len(transactions) < num_transactions * 2:
            iteration += 1
            
            # Random date within period
            days_offset = random.randint(0, days_in_period - 1)
            hours = random.randint(8, 22)
            minutes = random.choice([0, 15, 30, 45])
            txn_date = period_start + timedelta(days=days_offset, hours=hours, minutes=minutes)
            
            if txn_date > period_end:
                continue
            
            # Calculate remaining budget
            remaining_budget = budget - spent
            
            # Generate amount (don't exceed remaining budget)
            if remaining_budget < min_amount:
                break
            
            amount = random.uniform(min_amount, min(max_amount, remaining_budget * 1.1))
            
            # Select merchant
            merchant = random.choice(category_info['merchants'])
            
            # Generate description
            description = f"{merchant}"
            if category == 'Faturalar' and txn_date.day <= 10:
                description = f"{merchant} - {txn_date.strftime('%B %Y')}"
            
            # Create transaction
            txn = Transaction(
                user_id=user_id,
                statement_id=statement_id,
                date=txn_date,
                description=description,
                amount=amount,
                type='expense',
                category=category,
                merchant=merchant,
                account='Ana Hesap',
                reference_number=f'REF{random.randint(100000, 999999)}'
            )
            transactions.append(txn)
            spent += amount
        
        return transactions
    
    def _generate_seed(self, statement_id: str) -> int:
        """Generate a numeric seed from statement_id for consistent random generation"""
        # Use hash of statement_id to get consistent seed
        hash_obj = hashlib.md5(statement_id.encode())
        return int(hash_obj.hexdigest()[:8], 16)
    
    def _select_category(self, date: datetime) -> str:
        """Select category based on date patterns (legacy method, kept for compatibility)"""
        day_of_week = date.weekday()  # 0 = Monday, 6 = Sunday
        day_of_month = date.day
        
        # Bills on 1st-5th of month
        if 1 <= day_of_month <= 5:
            if random.random() < 0.3:  # 30% chance
                return 'Faturalar'
        
        # More entertainment on weekends
        if day_of_week >= 5:  # Saturday or Sunday
            if random.random() < 0.4:  # 40% chance
                return 'Eğlence'
        
        # Regular category selection weighted by frequency
        weights = {
            'Gıda': 0.35,  # Most common
            'Ulaşım': 0.20,
            'Alışveriş': 0.15,
            'Eğlence': 0.10,
            'Faturalar': 0.05,
            'Sağlık': 0.05,
            'Eğitim': 0.05,
            'Diğer': 0.05
        }
        
        return random.choices(list(weights.keys()), weights=list(weights.values()))[0]
