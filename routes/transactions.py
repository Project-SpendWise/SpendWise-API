from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import IntegrityError
import logging
import traceback
from datetime import datetime

from app import db
from models.transaction import Transaction
from models.statement import Statement
from models.user import User
from utils.responses import success_response, error_response

transactions_bp = Blueprint('transactions', __name__)
logger = logging.getLogger(__name__)

def get_db():
    """Get db instance from current app"""
    return current_app.extensions['sqlalchemy']


@transactions_bp.route('', methods=['GET'])
@jwt_required()
def get_transactions():
    """
    Get transactions with filtering.
    CRITICAL: If statementId query parameter is provided, return only transactions for that statement.
    """
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        # Get query parameters
        statement_id = request.args.get('statementId', '').strip()
        start_date_str = request.args.get('startDate', '').strip()
        end_date_str = request.args.get('endDate', '').strip()
        category = request.args.get('category', '').strip()
        account = request.args.get('account', '').strip()
        limit = min(request.args.get('limit', 50, type=int), 100)  # Max 100
        offset = max(request.args.get('offset', 0, type=int), 0)
        
        logger.debug(
            f"Get transactions request: statementId={statement_id}, "
            f"startDate={start_date_str}, endDate={end_date_str}, "
            f"category={category}, limit={limit}, offset={offset} ({user_id})"
        )
        
        # Build base query - always filter by user_id
        query = select(Transaction).filter_by(user_id=user_id)
        
        # CRITICAL: Filter by statementId if provided
        if statement_id:
            # Verify statement belongs to user
            statement = db_instance.session.get(Statement, statement_id)
            if not statement:
                return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
            if statement.user_id != user_id:
                return error_response('Access denied', 'FORBIDDEN', 403)
            query = query.filter_by(statement_id=statement_id)
        
        # Filter by date range
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                query = query.filter(Transaction.date >= start_date)
            except ValueError:
                return error_response('Invalid startDate format. Use ISO 8601 format.', 'INVALID_DATE', 400)
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                query = query.filter(Transaction.date <= end_date)
            except ValueError:
                return error_response('Invalid endDate format. Use ISO 8601 format.', 'INVALID_DATE', 400)
        
        # Filter by category
        if category:
            query = query.filter_by(category=category)
        
        # Filter by account
        if account:
            query = query.filter_by(account=account)
        
        # Get total count (before pagination)
        count_query = select(func.count(Transaction.id)).filter_by(user_id=user_id)
        if statement_id:
            count_query = count_query.filter_by(statement_id=statement_id)
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                count_query = count_query.filter(Transaction.date >= start_date)
            except ValueError:
                pass
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                count_query = count_query.filter(Transaction.date <= end_date)
            except ValueError:
                pass
        if category:
            count_query = count_query.filter_by(category=category)
        if account:
            count_query = count_query.filter_by(account=account)
        
        total_count = db_instance.session.scalar(count_query) or 0
        
        # Apply ordering (newest first) and pagination
        query = query.order_by(Transaction.date.desc()).offset(offset).limit(limit)
        
        # Execute query
        transactions = db_instance.session.scalars(query).all()
        
        # Convert to dict
        transactions_data = [txn.to_dict() for txn in transactions]
        
        logger.debug(f"Get transactions successful: {len(transactions_data)} transactions returned ({user_id})")
        return success_response(
            data={
                'transactions': transactions_data,
                'total': total_count,
                'limit': limit,
                'offset': offset
            }
        )
        
    except Exception as e:
        logger.error(
            f"Get transactions error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"User: {user_id}"
        )
        return error_response(
            'An error occurred while fetching transactions',
            'FETCH_ERROR',
            500
        )


@transactions_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_transaction_summary():
    """
    Get aggregated transaction summary.
    CRITICAL: If statementId is provided, calculate summary only for that statement's transactions.
    """
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        # Get query parameters
        statement_id = request.args.get('statementId', '').strip()
        start_date_str = request.args.get('startDate', '').strip()
        end_date_str = request.args.get('endDate', '').strip()
        
        logger.debug(
            f"Get transaction summary request: statementId={statement_id}, "
            f"startDate={start_date_str}, endDate={end_date_str} ({user_id})"
        )
        
        # Build base query
        income_query = select(func.sum(Transaction.amount)).filter_by(
            user_id=user_id,
            type='income'
        )
        expense_query = select(func.sum(Transaction.amount)).filter_by(
            user_id=user_id,
            type='expense'
        )
        count_query = select(func.count(Transaction.id)).filter_by(user_id=user_id)
        
        # CRITICAL: Filter by statementId if provided
        if statement_id:
            # Verify statement belongs to user
            statement = db_instance.session.get(Statement, statement_id)
            if not statement:
                return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
            if statement.user_id != user_id:
                return error_response('Access denied', 'FORBIDDEN', 403)
            
            income_query = income_query.filter_by(statement_id=statement_id)
            expense_query = expense_query.filter_by(statement_id=statement_id)
            count_query = count_query.filter_by(statement_id=statement_id)
            
            # Use statement period if no dates provided
            if not start_date_str and statement.statement_period_start:
                start_date_str = statement.statement_period_start.isoformat() + 'Z'
            if not end_date_str and statement.statement_period_end:
                end_date_str = statement.statement_period_end.isoformat() + 'Z'
        
        # Filter by date range
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                income_query = income_query.filter(Transaction.date >= start_date)
                expense_query = expense_query.filter(Transaction.date >= start_date)
                count_query = count_query.filter(Transaction.date >= start_date)
            except ValueError:
                return error_response('Invalid startDate format. Use ISO 8601 format.', 'INVALID_DATE', 400)
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                income_query = income_query.filter(Transaction.date <= end_date)
                expense_query = expense_query.filter(Transaction.date <= end_date)
                count_query = count_query.filter(Transaction.date <= end_date)
            except ValueError:
                return error_response('Invalid endDate format. Use ISO 8601 format.', 'INVALID_DATE', 400)
        
        # Execute queries
        total_income = db_instance.session.scalar(income_query) or 0.0
        total_expenses = db_instance.session.scalar(expense_query) or 0.0
        transaction_count = db_instance.session.scalar(count_query) or 0
        
        # Calculate savings
        savings = float(total_income) - float(total_expenses)
        
        # Determine period
        period = {}
        if start_date_str:
            try:
                period['start'] = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).isoformat() + 'Z'
            except ValueError:
                pass
        if end_date_str:
            try:
                period['end'] = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).isoformat() + 'Z'
            except ValueError:
                pass
        
        logger.debug(f"Get transaction summary successful: income={total_income}, expenses={total_expenses} ({user_id})")
        return success_response(
            data={
                'totalIncome': float(total_income),
                'totalExpenses': float(total_expenses),
                'savings': savings,
                'transactionCount': transaction_count,
                'period': period if period else None
            }
        )
        
    except Exception as e:
        logger.error(
            f"Get transaction summary error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"User: {user_id}"
        )
        return error_response(
            'An error occurred while fetching transaction summary',
            'FETCH_ERROR',
            500
        )
