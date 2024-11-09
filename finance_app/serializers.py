from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Category, CategoryPreference, Transaction,
    RecurringTransaction, Budget, SharedBudget, Notification
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'balance', 'global_notification_mode']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_default']


class CategoryPreferenceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = CategoryPreference
        fields = ['id', 'color', 'user', 'category']


class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'name', 'amount', 'created_at', 'performed_at', 'user', 'category', 'description']


class RecurringTransactionSerializer(TransactionSerializer):
    interval = serializers.CharField(source='interval.name', read_only=True)

    class Meta(TransactionSerializer.Meta):
        model = RecurringTransaction
        fields = TransactionSerializer.Meta.fields + ['interval']


class BudgetSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'owner', 'created_at', 'exceeded_at', 'limit',
            'period_start', 'period_end', 'description', 'categories'
        ]


class SharedBudgetSerializer(serializers.ModelSerializer):
    budget = BudgetSerializer(read_only=True)
    shared_with = UserSerializer(read_only=True)
    permission = serializers.CharField(source='permission.name', read_only=True)
    role = serializers.CharField(source='role.name', read_only=True)
    notification_mode = serializers.CharField(source='notification_mode.name', read_only=True)

    class Meta:
        model = SharedBudget
        fields = [
            'id', 'budget', 'shared_with', 'permission', 'role',
            'on_exceeded', 'on_limit_change', 'on_transaction', 'notification_mode'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'receiver', 'subject', 'message', 'sent_at', 'is_read']