"""
Period Analyzer Module
Groups transactions into periods based on income events
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PeriodAnalyzer:
    """Groups transactions into periods based on income events"""
    
    def __init__(self):
        """Initialize period analyzer"""
        pass
    
    def group_into_periods(
        self,
        transactions: List[Dict[str, Any]],
        income_transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Group transactions into periods based on income events
        
        Args:
            transactions: All transactions (sorted by date)
            income_transactions: List of detected income transactions
            
        Returns:
            List of period dictionaries
        """
        logger.info(f"Grouping {len(transactions)} transactions into periods based on {len(income_transactions)} income events")
        
        # Sort transactions by date
        sorted_transactions = sorted(
            transactions,
            key=lambda x: self._parse_date(x.get('date', ''))
        )
        
        # Sort income transactions by date
        sorted_income = sorted(
            income_transactions,
            key=lambda x: self._parse_date(x.get('date', ''))
        )
        
        periods = []
        
        if not sorted_income:
            # No income detected - create single period
            logger.warning("No income transactions detected, creating single period")
            start_date = self._parse_date(sorted_transactions[0].get('date', '')) if sorted_transactions else None
            end_date = self._parse_date(sorted_transactions[-1].get('date', '')) if sorted_transactions else None
            periods.append({
                'period_id': 'no-income',
                'start_date': start_date.isoformat() if start_date and start_date != datetime.min else None,
                'end_date': end_date.isoformat() if end_date and end_date != datetime.min else None,
                'income_amount': 0.0,
                'income_transaction': None,
                'transactions': sorted_transactions,
                'total_expenses': sum(abs(float(t.get('amount', 0))) for t in sorted_transactions if t.get('transaction_type') == 'debit'),
                'total_credits': sum(float(t.get('amount', 0)) for t in sorted_transactions if t.get('transaction_type') == 'credit'),
                'remaining_balance': 0.0
            })
            return periods
        
        # Create pre-income period (transactions before first income)
        first_income_date = self._parse_date(sorted_income[0].get('date', ''))
        pre_income_txns = [
            t for t in sorted_transactions
            if self._parse_date(t.get('date', '')) < first_income_date
        ]
        
        if pre_income_txns:
            start_date = self._parse_date(pre_income_txns[0].get('date', '')) if pre_income_txns else None
            end_date = self._parse_date(pre_income_txns[-1].get('date', '')) if pre_income_txns else None
            periods.append({
                'period_id': 'pre-income',
                'start_date': start_date.isoformat() if start_date and start_date != datetime.min else None,
                'end_date': end_date.isoformat() if end_date and end_date != datetime.min else None,
                'income_amount': 0.0,
                'income_transaction': None,
                'transactions': pre_income_txns,
                'total_expenses': sum(abs(float(t.get('amount', 0))) for t in pre_income_txns if t.get('transaction_type') == 'debit'),
                'total_credits': sum(float(t.get('amount', 0)) for t in pre_income_txns if t.get('transaction_type') == 'credit'),
                'remaining_balance': 0.0
            })
            logger.info(f"Created pre-income period with {len(pre_income_txns)} transactions")
        
        # Create periods between income events
        # Use balance tracking for accurate financial calculations
        for i, income_txn in enumerate(sorted_income):
            income_date = self._parse_date(income_txn.get('date', ''))
            income_amount = abs(float(income_txn.get('amount', 0)))
            
            # Get balance after income (this is the starting balance for the period)
            balance_after_income = income_txn.get('balance_after')
            if balance_after_income is not None:
                starting_balance = float(balance_after_income)
            else:
                # Calculate from previous period if available
                if i > 0 and periods:
                    prev_period = periods[-1]
                    prev_ending_balance = prev_period.get('ending_balance', 0.0)
                    starting_balance = prev_ending_balance + income_amount
                else:
                    # First period - estimate from income amount
                    starting_balance = income_amount
            
            # Determine period end date (next income date or last transaction)
            if i + 1 < len(sorted_income):
                next_income_date = self._parse_date(sorted_income[i + 1].get('date', ''))
                period_end = next_income_date
            else:
                # Last income - period ends at last transaction
                period_end = self._parse_date(sorted_transactions[-1].get('date', '')) if sorted_transactions else income_date
            
            # Get transactions in this period (excluding the income transaction itself for now)
            period_txns = [
                t for t in sorted_transactions
                if income_date < self._parse_date(t.get('date', '')) < period_end
            ]
            
            # Calculate financial metrics using code (not AI)
            total_expenses = sum(
                abs(float(t.get('amount', 0)))
                for t in period_txns
                if t.get('transaction_type') == 'debit'
            )
            
            # Other credits (non-income credits in this period)
            other_credits = sum(
                float(t.get('amount', 0))
                for t in period_txns
                if t.get('transaction_type') == 'credit'
            )
            
            # Calculate ending balance (code-based calculation)
            # Starting balance - expenses + other credits
            ending_balance = starting_balance - total_expenses + other_credits
            
            # Also calculate remaining from income perspective
            remaining_from_income = income_amount - total_expenses
            
            # Include the income transaction in the period transactions list
            all_period_txns = [income_txn] + period_txns
            all_period_txns.sort(key=lambda x: self._parse_date(x.get('date', '')))
            
            periods.append({
                'period_id': f'period-{i + 1}',
                'start_date': income_date.isoformat() if income_date and income_date != datetime.min else None,
                'end_date': period_end.isoformat() if period_end and period_end != datetime.min else None,
                'income_amount': income_amount,
                'income_transaction': income_txn,
                'starting_balance': starting_balance,  # Balance after income
                'ending_balance': ending_balance,  # Balance at end of period (before next income)
                'transactions': all_period_txns,
                'total_expenses': total_expenses,
                'other_credits': other_credits,  # Credits other than income
                'remaining_from_income': remaining_from_income  # Income - expenses
            })
            
            logger.info(
                f"Created period {i + 1}: {len(all_period_txns)} transactions, "
                f"income: {income_amount:.2f}, starting balance: {starting_balance:.2f}, "
                f"expenses: {total_expenses:.2f}, ending balance: {ending_balance:.2f}, "
                f"remaining from income: {remaining_from_income:.2f}"
            )
        
        return periods
    
    def _parse_date(self, date_str: Any) -> datetime:
        """
        Parse date string to datetime object
        
        Args:
            date_str: Date string or datetime object
            
        Returns:
            datetime object
        """
        if isinstance(date_str, datetime):
            return date_str
        
        if not date_str:
            return datetime.min
        
        # Try parsing common formats
        from dateutil import parser
        try:
            return parser.parse(str(date_str))
        except:
            logger.warning(f"Could not parse date: {date_str}, using min date")
            return datetime.min

