from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select, func, and_, extract, case
from sqlalchemy.exc import IntegrityError
import logging
import traceback
from datetime import datetime, timedelta
from collections import defaultdict

from app import db
from models.transaction import Transaction
from models.statement import Statement
from models.user import User
from utils.responses import success_response, error_response

analytics_bp = Blueprint('analytics', __name__)
logger = logging.getLogger(__name__)

def get_db():
    """Get db instance from current app"""
    return current_app.extensions['sqlalchemy']


def _get_base_transaction_query(user_id, statement_id=None, start_date=None, end_date=None):
    """Helper to build base transaction query with filters"""
    query = select(Transaction).filter_by(user_id=user_id, type='expense')
    
    if statement_id:
        query = query.filter_by(statement_id=statement_id)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    return query


def _parse_date_params(start_date_str, end_date_str, statement=None):
    """Parse and return date parameters, using statement period if available"""
    start_date = None
    end_date = None
    
    if statement and not start_date_str and statement.statement_period_start:
        start_date = statement.statement_period_start
    elif start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Invalid startDate format. Use ISO 8601 format.')
    
    if statement and not end_date_str and statement.statement_period_end:
        end_date = statement.statement_period_end
    elif end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Invalid endDate format. Use ISO 8601 format.')
    
    return start_date, end_date


@analytics_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_category_breakdown():
    """
    Get category breakdown with percentages.
    Supports statementId filtering.
    """
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        statement_id = request.args.get('statementId', '').strip()
        start_date_str = request.args.get('startDate', '').strip()
        end_date_str = request.args.get('endDate', '').strip()
        
        logger.debug(f"Get category breakdown: statementId={statement_id} ({user_id})")
        
        # Verify statement if provided
        statement = None
        if statement_id:
            statement = db_instance.session.get(Statement, statement_id)
            if not statement:
                return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
            if statement.user_id != user_id:
                return error_response('Access denied', 'FORBIDDEN', 403)
        
        start_date, end_date = _parse_date_params(start_date_str, end_date_str, statement)
        
        # Build query for category aggregation
        query = select(
            Transaction.category,
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('count')
        ).filter_by(
            user_id=user_id,
            type='expense'
        )
        
        if statement_id:
            query = query.filter_by(statement_id=statement_id)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        
        query = query.group_by(Transaction.category)
        query = query.order_by(func.sum(Transaction.amount).desc())
        
        results = db_instance.session.execute(query).all()
        
        # Calculate total expenses
        total_expenses = sum(float(row.total_amount) for row in results)
        
        # Build response
        categories = []
        for row in results:
            if row.category:  # Skip null categories
                percentage = (float(row.total_amount) / total_expenses * 100) if total_expenses > 0 else 0
                categories.append({
                    'category': row.category,
                    'totalAmount': float(row.total_amount),
                    'percentage': round(percentage, 1),
                    'transactionCount': row.count
                })
        
        logger.debug(f"Get category breakdown successful: {len(categories)} categories ({user_id})")
        # Frontend spec expects array directly, not wrapped in object
        return success_response(data=categories)
        
    except ValueError as e:
        return error_response(str(e), 'INVALID_DATE', 400)
    except Exception as e:
        logger.error(f"Get category breakdown error: {str(e)}\nTraceback: {traceback.format_exc()}")
        return error_response('An error occurred', 'SERVER_ERROR', 500)


@analytics_bp.route('/trends', methods=['GET'])
@jwt_required()
def get_spending_trends():
    """
    Get spending trends by day/week/month.
    Supports statementId filtering.
    """
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        statement_id = request.args.get('statementId', '').strip()
        start_date_str = request.args.get('startDate', '').strip()
        end_date_str = request.args.get('endDate', '').strip()
        period = request.args.get('period', 'day').strip()  # day, week, month
        
        logger.debug(f"Get spending trends: statementId={statement_id}, period={period} ({user_id})")
        
        # Verify statement if provided
        statement = None
        if statement_id:
            statement = db_instance.session.get(Statement, statement_id)
            if not statement:
                return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
            if statement.user_id != user_id:
                return error_response('Access denied', 'FORBIDDEN', 403)
        
        start_date, end_date = _parse_date_params(start_date_str, end_date_str, statement)
        
        # Build query
        if period == 'day':
            date_expr = func.date(Transaction.date)
        elif period == 'week':
            # Extract year and week
            date_expr = func.strftime('%Y-W%W', Transaction.date)
        elif period == 'month':
            date_expr = func.strftime('%Y-%m', Transaction.date)
        else:
            return error_response('period must be "day", "week", or "month"', 'INVALID_PERIOD', 400)
        
        # Get income and expenses separately for each period
        # Build income query
        income_query = select(
            date_expr.label('period_date'),
            func.sum(Transaction.amount).label('income')
        ).filter_by(
            user_id=user_id,
            type='income'
        )
        
        # Build expense query
        expense_query = select(
            date_expr.label('period_date'),
            func.sum(Transaction.amount).label('expenses')
        ).filter_by(
            user_id=user_id,
            type='expense'
        )
        
        if statement_id:
            income_query = income_query.filter_by(statement_id=statement_id)
            expense_query = expense_query.filter_by(statement_id=statement_id)
        
        if start_date:
            income_query = income_query.filter(Transaction.date >= start_date)
            expense_query = expense_query.filter(Transaction.date >= start_date)
        if end_date:
            income_query = income_query.filter(Transaction.date <= end_date)
            expense_query = expense_query.filter(Transaction.date <= end_date)
        
        income_query = income_query.group_by(date_expr).order_by(date_expr)
        expense_query = expense_query.group_by(date_expr).order_by(date_expr)
        
        income_results = db_instance.session.execute(income_query).all()
        expense_results = db_instance.session.execute(expense_query).all()
        
        # Combine results by period_date
        trends_dict = {}
        
        # Add income data
        for row in income_results:
            period_key = str(row.period_date)
            if period_key not in trends_dict:
                trends_dict[period_key] = {
                    'period_date': row.period_date,
                    'income': 0.0,
                    'expenses': 0.0
                }
            trends_dict[period_key]['income'] = float(row.income or 0)
        
        # Add expense data
        for row in expense_results:
            period_key = str(row.period_date)
            if period_key not in trends_dict:
                trends_dict[period_key] = {
                    'period_date': row.period_date,
                    'income': 0.0,
                    'expenses': 0.0
                }
            trends_dict[period_key]['expenses'] = float(row.expenses or 0)
        
        # Convert to list format matching spec
        trends = []
        for period_key in sorted(trends_dict.keys()):
            row = trends_dict[period_key]
            
            # Convert period_date to ISO format
            if period == 'day':
                period_date = datetime.strptime(str(row['period_date']), '%Y-%m-%d').isoformat() + 'Z'
            elif period == 'week':
                # Parse week format
                year, week = str(row['period_date']).split('-W')
                # Approximate to first day of week
                try:
                    period_date = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w').isoformat() + 'Z'
                except:
                    period_date = datetime.strptime(f'{year}-01-01', '%Y-%m-%d').isoformat() + 'Z'
            else:  # month
                period_date = datetime.strptime(str(row['period_date']), '%Y-%m').isoformat() + 'Z'
            
            income = row['income']
            expenses = row['expenses']
            savings = income - expenses
            
            trends.append({
                'date': period_date,
                'income': income,
                'expenses': expenses,
                'savings': savings
            })
        
        logger.debug(f"Get spending trends successful: {len(trends)} periods ({user_id})")
        return success_response(data=trends)
        
    except ValueError as e:
        return error_response(str(e), 'INVALID_DATE', 400)
    except Exception as e:
        logger.error(f"Get spending trends error: {str(e)}\nTraceback: {traceback.format_exc()}")
        return error_response('An error occurred', 'SERVER_ERROR', 500)


@analytics_bp.route('/insights', methods=['GET'])
@jwt_required()
def get_financial_insights():
    """
    Get financial insights.
    Supports statementId filtering.
    """
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        statement_id = request.args.get('statementId', '').strip()
        start_date_str = request.args.get('startDate', '').strip()
        end_date_str = request.args.get('endDate', '').strip()
        
        logger.debug(f"Get financial insights: statementId={statement_id} ({user_id})")
        
        # Verify statement if provided
        statement = None
        if statement_id:
            statement = db_instance.session.get(Statement, statement_id)
            if not statement:
                return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
            if statement.user_id != user_id:
                return error_response('Access denied', 'FORBIDDEN', 403)
        
        start_date, end_date = _parse_date_params(start_date_str, end_date_str, statement)
        
        # Calculate totals
        income_query = select(func.sum(Transaction.amount)).filter_by(user_id=user_id, type='income')
        expense_query = select(func.sum(Transaction.amount)).filter_by(user_id=user_id, type='expense')
        
        if statement_id:
            income_query = income_query.filter_by(statement_id=statement_id)
            expense_query = expense_query.filter_by(statement_id=statement_id)
        
        if start_date:
            income_query = income_query.filter(Transaction.date >= start_date)
            expense_query = expense_query.filter(Transaction.date >= start_date)
        if end_date:
            income_query = income_query.filter(Transaction.date <= end_date)
            expense_query = expense_query.filter(Transaction.date <= end_date)
        
        total_income = float(db_instance.session.scalar(income_query) or 0)
        total_expenses = float(db_instance.session.scalar(expense_query) or 0)
        
        # Calculate savings rate
        savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0.0
        
        # Get top spending category
        category_query = select(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter_by(
            user_id=user_id,
            type='expense'
        )
        
        if statement_id:
            category_query = category_query.filter_by(statement_id=statement_id)
        if start_date:
            category_query = category_query.filter(Transaction.date >= start_date)
        if end_date:
            category_query = category_query.filter(Transaction.date <= end_date)
        
        category_query = category_query.group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc())
        top_category_result = db_instance.session.execute(category_query).first()
        top_spending_category = top_category_result.category if top_category_result and top_category_result.category else None
        
        # Calculate average daily spending
        days_in_period = 1
        if start_date and end_date:
            days_in_period = max(1, (end_date - start_date).days + 1)
        elif statement:
            if statement.statement_period_start and statement.statement_period_end:
                days_in_period = max(1, (statement.statement_period_end - statement.statement_period_start).days + 1)
        average_daily_spending = total_expenses / days_in_period if days_in_period > 0 else 0.0
        
        # Get biggest expense
        biggest_expense_query = select(
            func.max(Transaction.amount).label('max_amount')
        ).filter_by(
            user_id=user_id,
            type='expense'
        )
        
        if statement_id:
            biggest_expense_query = biggest_expense_query.filter_by(statement_id=statement_id)
        if start_date:
            biggest_expense_query = biggest_expense_query.filter(Transaction.date >= start_date)
        if end_date:
            biggest_expense_query = biggest_expense_query.filter(Transaction.date <= end_date)
        
        biggest_expense = float(db_instance.session.scalar(biggest_expense_query) or 0.0)
        
        # Build recommendations array
        recommendations = []
        if savings_rate < 20 and savings_rate >= 0:
            recommendations.append(f"Your spending on {top_spending_category} is {savings_rate:.1f}% higher than average")
        if savings_rate < 0:
            recommendations.append("Your expenses exceed your income. Consider reviewing your spending habits.")
        if top_spending_category:
            recommendations.append(f"Consider setting a budget for {top_spending_category} category")
        
        logger.debug(f"Get financial insights successful ({user_id})")
        return success_response(data={
            'savingsRate': round(savings_rate, 1),
            'topSpendingCategory': top_spending_category,
            'averageDailySpending': round(average_daily_spending, 2),
            'biggestExpense': biggest_expense,
            'recommendations': recommendations
        })
        
    except ValueError as e:
        return error_response(str(e), 'INVALID_DATE', 400)
    except Exception as e:
        logger.error(f"Get financial insights error: {str(e)}\nTraceback: {traceback.format_exc()}")
        return error_response('An error occurred', 'SERVER_ERROR', 500)


@analytics_bp.route('/monthly-trends', methods=['GET'])
@jwt_required()
def get_monthly_trends():
    """
    Get monthly income/expenses/savings trends.
    Supports statementId filtering.
    """
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        statement_id = request.args.get('statementId', '').strip()
        months = min(request.args.get('months', 12, type=int), 24)  # Max 24 months
        
        logger.debug(f"Get monthly trends: statementId={statement_id}, months={months} ({user_id})")
        
        # Verify statement if provided
        if statement_id:
            statement = db_instance.session.get(Statement, statement_id)
            if not statement:
                return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
            if statement.user_id != user_id:
                return error_response('Access denied', 'FORBIDDEN', 403)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)  # Approximate
        
        # Build queries for monthly aggregation
        month_expr = func.strftime('%Y-%m', Transaction.date)
        
        income_query = select(
            month_expr.label('month'),
            func.sum(Transaction.amount).label('total')
        ).filter_by(
            user_id=user_id,
            type='income'
        )
        
        expense_query = select(
            month_expr.label('month'),
            func.sum(Transaction.amount).label('total')
        ).filter_by(
            user_id=user_id,
            type='expense'
        )
        
        if statement_id:
            income_query = income_query.filter_by(statement_id=statement_id)
            expense_query = expense_query.filter_by(statement_id=statement_id)
        
        income_query = income_query.filter(Transaction.date >= start_date)
        expense_query = expense_query.filter(Transaction.date >= start_date)
        
        income_query = income_query.group_by(month_expr).order_by(month_expr)
        expense_query = expense_query.group_by(month_expr).order_by(month_expr)
        
        income_results = {row.month: float(row.total) for row in db_instance.session.execute(income_query).all()}
        expense_results = {row.month: float(row.total) for row in db_instance.session.execute(expense_query).all()}
        
        # Combine results
        all_months = sorted(set(list(income_results.keys()) + list(expense_results.keys())))
        monthly_data = []
        
        for month in all_months:
            income = income_results.get(month, 0.0)
            expenses = expense_results.get(month, 0.0)
            savings = income - expenses
            
            monthly_data.append({
                'month': datetime.strptime(month, '%Y-%m').isoformat() + 'Z',
                'income': income,
                'expenses': expenses,
                'savings': savings
            })
        
        logger.debug(f"Get monthly trends successful: {len(monthly_data)} months ({user_id})")
        # Frontend spec expects array directly
        return success_response(data=monthly_data)
        
    except Exception as e:
        logger.error(f"Get monthly trends error: {str(e)}\nTraceback: {traceback.format_exc()}")
        return error_response('An error occurred', 'SERVER_ERROR', 500)


@analytics_bp.route('/category-trends', methods=['GET'])
@jwt_required()
def get_category_trends():
    """
    Get category trends over time.
    Supports statementId filtering.
    """
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        statement_id = request.args.get('statementId', '').strip()
        top_categories = min(request.args.get('topCategories', 5, type=int), 10)  # Max 10
        months = request.args.get('months', 12, type=int)
        
        logger.debug(f"Get category trends: statementId={statement_id}, top={top_categories} ({user_id})")
        
        # Verify statement if provided
        if statement_id:
            statement = db_instance.session.get(Statement, statement_id)
            if not statement:
                return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
            if statement.user_id != user_id:
                return error_response('Access denied', 'FORBIDDEN', 403)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)
        
        # Get top categories by total spending
        top_categories_query = select(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter_by(
            user_id=user_id,
            type='expense'
        )
        
        if statement_id:
            top_categories_query = top_categories_query.filter_by(statement_id=statement_id)
        
        top_categories_query = top_categories_query.filter(Transaction.date >= start_date)
        top_categories_query = top_categories_query.group_by(Transaction.category)
        top_categories_query = top_categories_query.order_by(func.sum(Transaction.amount).desc()).limit(top_categories)
        
        top_categories_list = [row.category for row in db_instance.session.execute(top_categories_query).all() if row.category]
        
        # Get monthly data for each category
        month_expr = func.strftime('%Y-%m', Transaction.date)
        category_trends = []
        
        for category in top_categories_list:
            query = select(
                month_expr.label('month'),
                func.sum(Transaction.amount).label('total')
            ).filter_by(
                user_id=user_id,
                type='expense',
                category=category
            )
            
            if statement_id:
                query = query.filter_by(statement_id=statement_id)
            
            query = query.filter(Transaction.date >= start_date)
            query = query.group_by(month_expr).order_by(month_expr)
            
            monthly_data = []
            for row in db_instance.session.execute(query).all():
                monthly_data.append({
                    'month': datetime.strptime(row.month, '%Y-%m').isoformat() + 'Z',
                    'amount': float(row.total)
                })
            
            category_trends.append({
                'categoryName': category,
                'monthlyData': monthly_data
            })
        
        logger.debug(f"Get category trends successful: {len(category_trends)} categories ({user_id})")
        return success_response(data={'categoryTrends': category_trends})
        
    except Exception as e:
        logger.error(f"Get category trends error: {str(e)}\nTraceback: {traceback.format_exc()}")
        return error_response('An error occurred', 'SERVER_ERROR', 500)


@analytics_bp.route('/weekly-patterns', methods=['GET'])
@jwt_required()
def get_weekly_patterns():
    """
    Get day-of-week spending patterns.
    Supports statementId filtering.
    """
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        statement_id = request.args.get('statementId', '').strip()
        weeks = request.args.get('weeks', 4, type=int)
        
        logger.debug(f"Get weekly patterns: statementId={statement_id}, weeks={weeks} ({user_id})")
        
        # Verify statement if provided
        if statement_id:
            statement = db_instance.session.get(Statement, statement_id)
            if not statement:
                return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
            if statement.user_id != user_id:
                return error_response('Access denied', 'FORBIDDEN', 403)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(weeks=weeks)
        
        # Get day of week (1=Monday, 7=Sunday using ISO 8601)
        # SQLite uses 0=Sunday, so we adjust
        day_of_week_expr = case(
            (extract('dow', Transaction.date) == 0, 7),  # Sunday = 7
            else_=extract('dow', Transaction.date) + 1
        )
        
        query = select(
            day_of_week_expr.label('day_of_week'),
            func.avg(Transaction.amount).label('avg_amount'),
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('count')
        ).filter_by(
            user_id=user_id,
            type='expense'
        )
        
        if statement_id:
            query = query.filter_by(statement_id=statement_id)
        
        query = query.filter(Transaction.date >= start_date)
        query = query.group_by(day_of_week_expr)
        query = query.order_by(day_of_week_expr)
        
        results = db_instance.session.execute(query).all()
        
        day_names = {
            1: 'Monday',
            2: 'Tuesday',
            3: 'Wednesday',
            4: 'Thursday',
            5: 'Friday',
            6: 'Saturday',
            7: 'Sunday'
        }
        
        patterns = []
        for row in results:
            day_num = int(row.day_of_week)
            patterns.append({
                'dayOfWeek': day_num,
                'dayName': day_names.get(day_num, 'Unknown'),
                'averageSpending': float(row.avg_amount),
                'transactionCount': row.count
            })
        
        logger.debug(f"Get weekly patterns successful: {len(patterns)} patterns ({user_id})")
        return success_response(data={'patterns': patterns})
        
    except Exception as e:
        logger.error(f"Get weekly patterns error: {str(e)}\nTraceback: {traceback.format_exc()}")
        return error_response('An error occurred', 'SERVER_ERROR', 500)


@analytics_bp.route('/year-over-year', methods=['GET'])
@jwt_required()
def get_year_over_year():
    """
    Get year-over-year comparison.
    Supports statementId filtering.
    """
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        statement_id = request.args.get('statementId', '').strip()
        year = request.args.get('year', datetime.utcnow().year, type=int)
        
        logger.debug(f"Get year-over-year: statementId={statement_id}, year={year} ({user_id})")
        
        # Verify statement if provided
        if statement_id:
            statement = db_instance.session.get(Statement, statement_id)
            if not statement:
                return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
            if statement.user_id != user_id:
                return error_response('Access denied', 'FORBIDDEN', 403)
        
        # Build queries for current and previous year
        month_expr = func.strftime('%Y-%m', Transaction.date)
        
        current_year_query = select(
            month_expr.label('month'),
            func.sum(Transaction.amount).label('total')
        ).filter_by(
            user_id=user_id,
            type='expense'
        )
        
        previous_year_query = select(
            month_expr.label('month'),
            func.sum(Transaction.amount).label('total')
        ).filter_by(
            user_id=user_id,
            type='expense'
        )
        
        if statement_id:
            current_year_query = current_year_query.filter_by(statement_id=statement_id)
            previous_year_query = previous_year_query.filter_by(statement_id=statement_id)
        
        # Filter by year
        current_start = datetime(year, 1, 1)
        current_end = datetime(year, 12, 31, 23, 59, 59)
        previous_start = datetime(year - 1, 1, 1)
        previous_end = datetime(year - 1, 12, 31, 23, 59, 59)
        
        current_year_query = current_year_query.filter(
            and_(Transaction.date >= current_start, Transaction.date <= current_end)
        )
        previous_year_query = previous_year_query.filter(
            and_(Transaction.date >= previous_start, Transaction.date <= previous_end)
        )
        
        current_year_query = current_year_query.group_by(month_expr).order_by(month_expr)
        previous_year_query = previous_year_query.group_by(month_expr).order_by(month_expr)
        
        current_results = {row.month: float(row.total) for row in db_instance.session.execute(current_year_query).all()}
        previous_results = {row.month: float(row.total) for row in db_instance.session.execute(previous_year_query).all()}
        
        # Combine results
        all_months = sorted(set(list(current_results.keys()) + list(previous_results.keys())))
        comparisons = []
        
        for month in all_months:
            current = current_results.get(month, 0.0)
            previous = previous_results.get(month, 0.0)
            
            change_percent = ((current - previous) / previous * 100) if previous > 0 else 0
            
            comparisons.append({
                'month': datetime.strptime(month, '%Y-%m').isoformat() + 'Z',
                'currentYear': current,
                'previousYear': previous,
                'changePercent': round(change_percent, 2)
            })
        
        logger.debug(f"Get year-over-year successful: {len(comparisons)} comparisons ({user_id})")
        return success_response(data={'comparisons': comparisons})
        
    except Exception as e:
        logger.error(f"Get year-over-year error: {str(e)}\nTraceback: {traceback.format_exc()}")
        return error_response('An error occurred', 'SERVER_ERROR', 500)


@analytics_bp.route('/forecast', methods=['GET'])
@jwt_required()
def get_spending_forecast():
    """
    Get spending forecast for next month.
    Supports statementId filtering.
    """
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        statement_id = request.args.get('statementId', '').strip()
        
        logger.debug(f"Get spending forecast: statementId={statement_id} ({user_id})")
        
        # Verify statement if provided
        if statement_id:
            statement = db_instance.session.get(Statement, statement_id)
            if not statement:
                return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
            if statement.user_id != user_id:
                return error_response('Access denied', 'FORBIDDEN', 403)
        
        # Get last 3 months of data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        
        # Get monthly averages by category
        month_expr = func.strftime('%Y-%m', Transaction.date)
        
        query = select(
            Transaction.category,
            month_expr.label('month'),
            func.sum(Transaction.amount).label('total')
        ).filter_by(
            user_id=user_id,
            type='expense'
        )
        
        if statement_id:
            query = query.filter_by(statement_id=statement_id)
        
        query = query.filter(Transaction.date >= start_date)
        query = query.group_by(Transaction.category, month_expr)
        
        results = db_instance.session.execute(query).all()
        
        # Calculate averages by category
        category_totals = defaultdict(list)
        for row in results:
            if row.category:
                category_totals[row.category].append(float(row.total))
        
        # Calculate average per category
        by_category = {}
        for category, amounts in category_totals.items():
            avg = sum(amounts) / len(amounts) if amounts else 0
            by_category[category] = round(avg, 2)
        
        # Calculate total predicted spending
        predicted_spending = sum(by_category.values())
        
        # Next month
        next_month = (end_date.replace(day=1) + timedelta(days=32)).replace(day=1)
        
        logger.debug(f"Get spending forecast successful: predicted={predicted_spending} ({user_id})")
        return success_response(data={
            'forecast': {
                'nextMonth': next_month.isoformat() + 'Z',
                'predictedSpending': round(predicted_spending, 2),
                'confidence': 0.85,
                'byCategory': by_category,
                'method': 'moving_average',
                'monthsAnalyzed': 3
            }
        })
        
    except Exception as e:
        logger.error(f"Get spending forecast error: {str(e)}\nTraceback: {traceback.format_exc()}")
        return error_response('An error occurred', 'SERVER_ERROR', 500)
