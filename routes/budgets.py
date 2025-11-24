from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
import logging
import traceback
from datetime import datetime, timedelta

from app import db
from models.budget import Budget
from models.transaction import Transaction
from models.statement import Statement
from models.user import User
from utils.responses import success_response, error_response

budgets_bp = Blueprint('budgets', __name__)
logger = logging.getLogger(__name__)

def get_db():
    """Get db instance from current app"""
    return current_app.extensions['sqlalchemy']


@budgets_bp.route('', methods=['POST'])
@jwt_required()
def create_or_update_budget():
    """Create or update a budget for a category"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.info(f"Create/update budget request: {user_id}")
        
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 'INVALID_REQUEST', 400)
        
        category_id = data.get('categoryId')
        category_name = data.get('categoryName')
        amount = data.get('amount')
        period = data.get('period')
        start_date_str = data.get('startDate')
        
        # Validate required fields
        if not category_id or not category_name or amount is None or not period or not start_date_str:
            return error_response(
                'categoryId, categoryName, amount, period, and startDate are required',
                'MISSING_FIELDS',
                400
            )
        
        # Validate period
        if period not in ['monthly', 'yearly']:
            return error_response('period must be "monthly" or "yearly"', 'INVALID_PERIOD', 400)
        
        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                return error_response('amount must be greater than 0', 'INVALID_AMOUNT', 400)
        except (ValueError, TypeError):
            return error_response('amount must be a valid number', 'INVALID_AMOUNT', 400)
        
        # Parse start date
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        except ValueError:
            return error_response('Invalid startDate format. Use ISO 8601 format.', 'INVALID_DATE', 400)
        
        # Calculate end date based on period
        if period == 'monthly':
            end_date = start_date + timedelta(days=32)  # Approximate, will be adjusted
            end_date = end_date.replace(day=1) - timedelta(days=1)  # Last day of month
        else:  # yearly
            end_date = start_date.replace(month=12, day=31)
        
        # Check if budget already exists for this user, category, and period
        existing_budget = db_instance.session.scalar(
            select(Budget).filter_by(
                user_id=user_id,
                category_id=category_id,
                period=period
            )
        )
        
        if existing_budget:
            # Update existing budget
            existing_budget.category_name = category_name
            existing_budget.amount = amount
            existing_budget.start_date = start_date
            existing_budget.end_date = end_date
            existing_budget.updated_at = datetime.utcnow()
            budget = existing_budget
            logger.info(f"Budget updated: {budget.id} ({user_id})")
        else:
            # Create new budget
            budget = Budget(
                user_id=user_id,
                category_id=category_id,
                category_name=category_name,
                amount=amount,
                period=period,
                start_date=start_date,
                end_date=end_date
            )
            db_instance.session.add(budget)
            logger.info(f"Budget created: {budget.id} ({user_id})")
        
        db_instance.session.commit()
        
        return success_response(
            data=budget.to_dict(),
            message='Budget saved successfully',
            status_code=200
        )
        
    except IntegrityError as e:
        db_instance.session.rollback()
        logger.error(f"Budget create/update failed: Database integrity error - {str(e)} ({user_id})")
        return error_response('Failed to save budget', 'DATABASE_ERROR', 500)
    except Exception as e:
        db_instance.session.rollback()
        logger.error(
            f"Budget create/update error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"User: {user_id}"
        )
        return error_response('An error occurred', 'SERVER_ERROR', 500)


@budgets_bp.route('', methods=['GET'])
@jwt_required()
def list_budgets():
    """Get all budgets for the authenticated user"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        # Get query parameters
        period = request.args.get('period', '').strip()
        category_id = request.args.get('categoryId', '').strip()
        
        logger.debug(f"List budgets request: period={period}, categoryId={category_id} ({user_id})")
        
        # Build query
        query = select(Budget).filter_by(user_id=user_id)
        
        if period:
            query = query.filter_by(period=period)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # Order by start date
        query = query.order_by(Budget.start_date.desc())
        
        # Execute query
        budgets = db_instance.session.scalars(query).all()
        
        # Convert to dict
        budgets_data = [budget.to_dict() for budget in budgets]
        
        logger.debug(f"List budgets successful: {len(budgets_data)} budgets returned ({user_id})")
        return success_response(data={'budgets': budgets_data})
        
    except Exception as e:
        logger.error(
            f"List budgets error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"User: {user_id}"
        )
        return error_response('An error occurred while listing budgets', 'LIST_ERROR', 500)


@budgets_bp.route('/compare', methods=['GET'])
@jwt_required()
def compare_budgets():
    """
    Get budget comparison for current period.
    CRITICAL: If statementId is provided, compare against that statement's transactions only.
    """
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        
        # Get query parameters
        statement_id = request.args.get('statementId', '').strip()
        period = request.args.get('period', 'monthly').strip()
        start_date_str = request.args.get('startDate', '').strip()
        end_date_str = request.args.get('endDate', '').strip()
        
        logger.debug(
            f"Compare budgets request: statementId={statement_id}, period={period}, "
            f"startDate={start_date_str}, endDate={end_date_str} ({user_id})"
        )
        
        # CRITICAL: Filter by statementId if provided
        if statement_id:
            # Verify statement belongs to user
            statement = db_instance.session.get(Statement, statement_id)
            if not statement:
                return error_response('Statement not found', 'STATEMENT_NOT_FOUND', 404)
            if statement.user_id != user_id:
                return error_response('Access denied', 'FORBIDDEN', 403)
            
            # Use statement period if no dates provided
            if not start_date_str and statement.statement_period_start:
                start_date_str = statement.statement_period_start.isoformat() + 'Z'
            if not end_date_str and statement.statement_period_end:
                end_date_str = statement.statement_period_end.isoformat() + 'Z'
        
        # Determine date range
        if not start_date_str or not end_date_str:
            # Default to current month
            now = datetime.utcnow()
            if not start_date_str:
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                start_date_str = start_date.isoformat() + 'Z'
            if not end_date_str:
                if period == 'monthly':
                    # Last day of current month
                    if now.month == 12:
                        end_date = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
                    else:
                        end_date = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
                else:  # yearly
                    end_date = now.replace(month=12, day=31)
                end_date = end_date.replace(hour=23, minute=59, second=59)
                end_date_str = end_date.isoformat() + 'Z'
        
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        except ValueError:
            return error_response('Invalid date format. Use ISO 8601 format.', 'INVALID_DATE', 400)
        
        # Get all budgets for user and period
        budgets = db_instance.session.scalars(
            select(Budget).filter_by(user_id=user_id, period=period)
        ).all()
        
        comparisons = []
        
        for budget in budgets:
            # Calculate actual spending for this category
            spending_query = select(func.sum(Transaction.amount)).filter_by(
                user_id=user_id,
                category=budget.category_name,
                type='expense'
            ).filter(
                and_(
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                )
            )
            
            # CRITICAL: Filter by statementId if provided
            if statement_id:
                spending_query = spending_query.filter_by(statement_id=statement_id)
            
            actual_spending = db_instance.session.scalar(spending_query) or 0.0
            actual_spending = float(actual_spending)
            
            # Calculate metrics
            remaining = float(budget.amount) - actual_spending
            percentage_used = (actual_spending / float(budget.amount) * 100) if float(budget.amount) > 0 else 0
            is_over_budget = actual_spending > float(budget.amount)
            
            # Determine status
            if is_over_budget:
                status = 'over_budget'
            elif percentage_used >= 80:
                status = 'approaching_budget'
            else:
                status = 'on_track'
            
            comparisons.append({
                'budget': {
                    'id': budget.id,
                    'categoryId': budget.category_id,
                    'categoryName': budget.category_name,
                    'amount': float(budget.amount)
                },
                'actualSpending': actual_spending,
                'remaining': remaining,
                'percentageUsed': round(percentage_used, 2),
                'isOverBudget': is_over_budget,
                'status': status
            })
        
        logger.debug(f"Compare budgets successful: {len(comparisons)} comparisons ({user_id})")
        return success_response(
            data={
                'comparisons': comparisons,
                'period': {
                    'start': start_date_str,
                    'end': end_date_str
                }
            }
        )
        
    except Exception as e:
        logger.error(
            f"Compare budgets error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"User: {user_id}"
        )
        return error_response('An error occurred while comparing budgets', 'COMPARE_ERROR', 500)


@budgets_bp.route('/<budget_id>', methods=['DELETE'])
@jwt_required()
def delete_budget(budget_id):
    """Delete a budget"""
    try:
        db_instance = get_db()
        user_id = get_jwt_identity()
        logger.info(f"Budget delete request: {budget_id} ({user_id})")
        
        # Get budget
        budget = db_instance.session.get(Budget, budget_id)
        
        if not budget:
            logger.warning(f"Budget delete failed: Budget not found - {budget_id} ({user_id})")
            return error_response('Budget not found', 'BUDGET_NOT_FOUND', 404)
        
        # Verify ownership
        if budget.user_id != user_id:
            logger.warning(f"Budget delete failed: Access denied - {budget_id} ({user_id})")
            return error_response(
                'You do not have permission to delete this budget',
                'FORBIDDEN',
                403
            )
        
        # Delete budget
        db_instance.session.delete(budget)
        db_instance.session.commit()
        
        logger.info(f"Budget deleted successfully: {budget_id} ({user_id})")
        return success_response(
            data={'success': True, 'message': 'Budget deleted successfully'}
        )
        
    except Exception as e:
        db_instance.session.rollback()
        logger.error(
            f"Budget delete error: {str(e)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            f"Budget: {budget_id}, User: {user_id}"
        )
        return error_response('An error occurred during deletion', 'DELETE_ERROR', 500)
