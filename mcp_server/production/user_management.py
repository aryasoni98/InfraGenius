#!/usr/bin/env python3
"""
User Management System for DevOps/SRE MCP Server
Handles authentication, authorization, rate limiting, and usage tracking
"""

import asyncio
import time
import json
import hashlib
import jwt
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from contextlib import asynccontextmanager

# User tier definitions
class UserTier(Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

@dataclass
class TierLimits:
    monthly_limit: int
    hourly_limit: int
    concurrent_requests: int
    features: List[str]
    priority: int
    price: float

@dataclass
class User:
    user_id: str
    email: str
    tier: UserTier
    api_key: str
    created_at: datetime
    last_active: datetime
    monthly_usage: int = 0
    total_usage: int = 0
    subscription_end: Optional[datetime] = None
    is_active: bool = True

@dataclass
class UsageRecord:
    user_id: str
    timestamp: datetime
    endpoint: str
    processing_time: float
    tokens_used: int
    cost: float

class UserManager:
    """Comprehensive user management system"""
    
    # Tier configurations
    TIER_CONFIGS = {
        UserTier.FREE: TierLimits(
            monthly_limit=50,
            hourly_limit=10,
            concurrent_requests=2,
            features=['basic_analysis', 'devops', 'sre'],
            priority=1,
            price=0.0
        ),
        UserTier.STARTER: TierLimits(
            monthly_limit=500,
            hourly_limit=100,
            concurrent_requests=5,
            features=['all_analysis', 'priority_support', 'cloud', 'platform'],
            priority=2,
            price=10.0
        ),
        UserTier.PROFESSIONAL: TierLimits(
            monthly_limit=2500,
            hourly_limit=500,
            concurrent_requests=10,
            features=['advanced_features', 'custom_integrations', 'api_access'],
            priority=3,
            price=50.0
        ),
        UserTier.ENTERPRISE: TierLimits(
            monthly_limit=10000,
            hourly_limit=2000,
            concurrent_requests=25,
            features=['all_features', 'dedicated_support', 'sla', 'custom_models'],
            priority=4,
            price=200.0
        ),
        UserTier.CUSTOM: TierLimits(
            monthly_limit=999999,
            hourly_limit=10000,
            concurrent_requests=100,
            features=['unlimited', 'on_premise', 'custom_deployment'],
            priority=5,
            price=0.0  # Custom pricing
        )
    }
    
    def __init__(self, redis_url: str = "redis://localhost:6379", jwt_secret: str = None):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.jwt_secret = jwt_secret or "your-super-secret-jwt-key-change-in-production"
        self.logger = logging.getLogger(__name__)
        
    async def create_user(self, email: str, tier: UserTier = UserTier.FREE) -> User:
        """Create a new user account"""
        user_id = hashlib.sha256(f"{email}{time.time()}".encode()).hexdigest()[:16]
        api_key = self._generate_api_key(user_id)
        
        user = User(
            user_id=user_id,
            email=email,
            tier=tier,
            api_key=api_key,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        
        # Store user in Redis
        user_key = f"user:{user_id}"
        self.redis_client.hset(user_key, mapping=self._user_to_dict(user))
        
        # Create email-to-userid mapping
        self.redis_client.set(f"email:{email}", user_id)
        
        # Initialize usage counters
        self._init_usage_counters(user_id)
        
        self.logger.info(f"Created user {user_id} with tier {tier.value}")
        return user
    
    async def authenticate_user(self, api_key: str) -> Optional[User]:
        """Authenticate user by API key"""
        try:
            # Extract user_id from API key
            payload = jwt.decode(api_key, self.jwt_secret, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return None
                
            return await self.get_user(user_id)
            
        except jwt.InvalidTokenError:
            return None
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_key = f"user:{user_id}"
        user_data = self.redis_client.hgetall(user_key)
        
        if not user_data:
            return None
            
        return self._dict_to_user(user_data)
    
    async def check_rate_limit(self, user_id: str) -> Tuple[bool, Dict[str, int]]:
        """Check if user is within rate limits"""
        user = await self.get_user(user_id)
        if not user:
            return False, {}
            
        limits = self.TIER_CONFIGS[user.tier]
        
        # Check monthly limit
        monthly_usage = self._get_monthly_usage(user_id)
        if monthly_usage >= limits.monthly_limit:
            return False, {
                'monthly_used': monthly_usage,
                'monthly_limit': limits.monthly_limit,
                'reset_time': self._get_month_reset_time()
            }
        
        # Check hourly limit
        hourly_usage = self._get_hourly_usage(user_id)
        if hourly_usage >= limits.hourly_limit:
            return False, {
                'hourly_used': hourly_usage,
                'hourly_limit': limits.hourly_limit,
                'reset_time': self._get_hour_reset_time()
            }
        
        # Check concurrent requests
        concurrent_count = self._get_concurrent_requests(user_id)
        if concurrent_count >= limits.concurrent_requests:
            return False, {
                'concurrent_count': concurrent_count,
                'concurrent_limit': limits.concurrent_requests
            }
        
        return True, {
            'monthly_used': monthly_usage,
            'monthly_limit': limits.monthly_limit,
            'hourly_used': hourly_usage,
            'hourly_limit': limits.hourly_limit,
            'concurrent_count': concurrent_count,
            'concurrent_limit': limits.concurrent_requests
        }
    
    async def record_usage(self, user_id: str, endpoint: str, processing_time: float, tokens_used: int = 1):
        """Record API usage for billing and analytics"""
        # Increment usage counters
        self._increment_usage(user_id)
        
        # Calculate cost based on tier and usage
        user = await self.get_user(user_id)
        cost = self._calculate_cost(user.tier, tokens_used, processing_time)
        
        # Record usage details
        usage_record = UsageRecord(
            user_id=user_id,
            timestamp=datetime.utcnow(),
            endpoint=endpoint,
            processing_time=processing_time,
            tokens_used=tokens_used,
            cost=cost
        )
        
        # Store in Redis for analytics
        usage_key = f"usage:{user_id}:{int(time.time())}"
        self.redis_client.hset(usage_key, mapping=asdict(usage_record))
        self.redis_client.expire(usage_key, 86400 * 30)  # Keep for 30 days
        
        # Update user's last active time
        await self._update_last_active(user_id)
        
        return usage_record
    
    @asynccontextmanager
    async def track_concurrent_request(self, user_id: str):
        """Context manager to track concurrent requests"""
        concurrent_key = f"concurrent:{user_id}"
        try:
            # Increment concurrent counter
            self.redis_client.incr(concurrent_key)
            self.redis_client.expire(concurrent_key, 300)  # 5 minute timeout
            yield
        finally:
            # Decrement concurrent counter
            current_count = self.redis_client.get(concurrent_key)
            if current_count and int(current_count) > 0:
                self.redis_client.decr(concurrent_key)
    
    async def upgrade_user(self, user_id: str, new_tier: UserTier) -> bool:
        """Upgrade user to a different tier"""
        user = await self.get_user(user_id)
        if not user:
            return False
            
        user.tier = new_tier
        user_key = f"user:{user_id}"
        self.redis_client.hset(user_key, "tier", new_tier.value)
        
        self.logger.info(f"Upgraded user {user_id} to {new_tier.value}")
        return True
    
    async def get_usage_analytics(self, user_id: str, days: int = 30) -> Dict:
        """Get usage analytics for a user"""
        # Get usage records from the last N days
        start_time = int((datetime.utcnow() - timedelta(days=days)).timestamp())
        end_time = int(datetime.utcnow().timestamp())
        
        usage_pattern = f"usage:{user_id}:*"
        usage_keys = self.redis_client.keys(usage_pattern)
        
        # Filter by time range
        relevant_keys = []
        for key in usage_keys:
            timestamp = int(key.split(':')[-1])
            if start_time <= timestamp <= end_time:
                relevant_keys.append(key)
        
        # Aggregate analytics
        total_requests = len(relevant_keys)
        total_processing_time = 0
        total_cost = 0
        endpoint_usage = {}
        
        for key in relevant_keys:
            usage_data = self.redis_client.hgetall(key)
            total_processing_time += float(usage_data.get('processing_time', 0))
            total_cost += float(usage_data.get('cost', 0))
            
            endpoint = usage_data.get('endpoint', 'unknown')
            endpoint_usage[endpoint] = endpoint_usage.get(endpoint, 0) + 1
        
        return {
            'user_id': user_id,
            'period_days': days,
            'total_requests': total_requests,
            'total_processing_time': total_processing_time,
            'total_cost': total_cost,
            'avg_processing_time': total_processing_time / max(total_requests, 1),
            'endpoint_usage': endpoint_usage,
            'current_tier': (await self.get_user(user_id)).tier.value
        }
    
    def _generate_api_key(self, user_id: str) -> str:
        """Generate JWT-based API key"""
        payload = {
            'user_id': user_id,
            'issued_at': datetime.utcnow().timestamp(),
            'expires_at': (datetime.utcnow() + timedelta(days=365)).timestamp()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def _user_to_dict(self, user: User) -> Dict:
        """Convert User object to dictionary for Redis storage"""
        return {
            'user_id': user.user_id,
            'email': user.email,
            'tier': user.tier.value,
            'api_key': user.api_key,
            'created_at': user.created_at.isoformat(),
            'last_active': user.last_active.isoformat(),
            'monthly_usage': str(user.monthly_usage),
            'total_usage': str(user.total_usage),
            'subscription_end': user.subscription_end.isoformat() if user.subscription_end else '',
            'is_active': str(user.is_active)
        }
    
    def _dict_to_user(self, data: Dict) -> User:
        """Convert dictionary from Redis to User object"""
        return User(
            user_id=data['user_id'],
            email=data['email'],
            tier=UserTier(data['tier']),
            api_key=data['api_key'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_active=datetime.fromisoformat(data['last_active']),
            monthly_usage=int(data.get('monthly_usage', 0)),
            total_usage=int(data.get('total_usage', 0)),
            subscription_end=datetime.fromisoformat(data['subscription_end']) if data.get('subscription_end') else None,
            is_active=data.get('is_active', 'True') == 'True'
        )
    
    def _init_usage_counters(self, user_id: str):
        """Initialize usage counters for a new user"""
        current_month = datetime.utcnow().strftime('%Y-%m')
        current_hour = datetime.utcnow().strftime('%Y-%m-%d-%H')
        
        monthly_key = f"usage_monthly:{user_id}:{current_month}"
        hourly_key = f"usage_hourly:{user_id}:{current_hour}"
        
        self.redis_client.set(monthly_key, 0, ex=86400 * 32)  # Expire after month + buffer
        self.redis_client.set(hourly_key, 0, ex=3600)  # Expire after hour
    
    def _get_monthly_usage(self, user_id: str) -> int:
        """Get current month usage for user"""
        current_month = datetime.utcnow().strftime('%Y-%m')
        monthly_key = f"usage_monthly:{user_id}:{current_month}"
        return int(self.redis_client.get(monthly_key) or 0)
    
    def _get_hourly_usage(self, user_id: str) -> int:
        """Get current hour usage for user"""
        current_hour = datetime.utcnow().strftime('%Y-%m-%d-%H')
        hourly_key = f"usage_hourly:{user_id}:{current_hour}"
        return int(self.redis_client.get(hourly_key) or 0)
    
    def _get_concurrent_requests(self, user_id: str) -> int:
        """Get current concurrent request count"""
        concurrent_key = f"concurrent:{user_id}"
        return int(self.redis_client.get(concurrent_key) or 0)
    
    def _increment_usage(self, user_id: str):
        """Increment usage counters"""
        current_month = datetime.utcnow().strftime('%Y-%m')
        current_hour = datetime.utcnow().strftime('%Y-%m-%d-%H')
        
        monthly_key = f"usage_monthly:{user_id}:{current_month}"
        hourly_key = f"usage_hourly:{user_id}:{current_hour}"
        
        # Increment counters
        self.redis_client.incr(monthly_key)
        self.redis_client.incr(hourly_key)
        
        # Set expiration if new keys
        self.redis_client.expire(monthly_key, 86400 * 32)
        self.redis_client.expire(hourly_key, 3600)
    
    def _calculate_cost(self, tier: UserTier, tokens_used: int, processing_time: float) -> float:
        """Calculate cost for API usage"""
        # Base cost per request
        base_costs = {
            UserTier.FREE: 0.0,
            UserTier.STARTER: 0.02,
            UserTier.PROFESSIONAL: 0.05,
            UserTier.ENTERPRISE: 0.10,
            UserTier.CUSTOM: 0.15
        }
        
        base_cost = base_costs[tier]
        
        # Additional cost for processing time (for GPU usage)
        time_cost = processing_time * 0.001  # $0.001 per second
        
        # Additional cost for token usage
        token_cost = tokens_used * 0.0001  # $0.0001 per token
        
        return base_cost + time_cost + token_cost
    
    def _get_month_reset_time(self) -> int:
        """Get timestamp when monthly limit resets"""
        next_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if next_month.month == 12:
            next_month = next_month.replace(year=next_month.year + 1, month=1)
        else:
            next_month = next_month.replace(month=next_month.month + 1)
        return int(next_month.timestamp())
    
    def _get_hour_reset_time(self) -> int:
        """Get timestamp when hourly limit resets"""
        next_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        return int(next_hour.timestamp())
    
    async def _update_last_active(self, user_id: str):
        """Update user's last active timestamp"""
        user_key = f"user:{user_id}"
        self.redis_client.hset(user_key, "last_active", datetime.utcnow().isoformat())

class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
        
    async def __call__(self, request, call_next):
        # Extract API key from headers
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not api_key:
            return {"error": "API key required", "status_code": 401}
        
        # Authenticate user
        user = await self.user_manager.authenticate_user(api_key)
        if not user:
            return {"error": "Invalid API key", "status_code": 401}
        
        # Check rate limits
        allowed, limits = await self.user_manager.check_rate_limit(user.user_id)
        if not allowed:
            return {
                "error": "Rate limit exceeded",
                "status_code": 429,
                "limits": limits
            }
        
        # Track concurrent request
        async with self.user_manager.track_concurrent_request(user.user_id):
            # Process request
            start_time = time.time()
            response = await call_next(request)
            processing_time = time.time() - start_time
            
            # Record usage
            await self.user_manager.record_usage(
                user.user_id,
                str(request.url.path),
                processing_time
            )
            
            # Add usage headers to response
            response.headers['X-RateLimit-Remaining-Monthly'] = str(limits.get('monthly_limit', 0) - limits.get('monthly_used', 0))
            response.headers['X-RateLimit-Remaining-Hourly'] = str(limits.get('hourly_limit', 0) - limits.get('hourly_used', 0))
            
            return response

# Example usage and testing
async def demo_user_management():
    """Demo the user management system"""
    print("🔐 User Management System Demo")
    print("=" * 40)
    
    # Initialize user manager
    user_manager = UserManager()
    
    # Create test users
    free_user = await user_manager.create_user("free@example.com", UserTier.FREE)
    starter_user = await user_manager.create_user("starter@example.com", UserTier.STARTER)
    
    print(f"✅ Created free user: {free_user.user_id}")
    print(f"✅ Created starter user: {starter_user.user_id}")
    
    # Test authentication
    auth_user = await user_manager.authenticate_user(free_user.api_key)
    print(f"✅ Authentication successful: {auth_user.email}")
    
    # Test rate limiting
    allowed, limits = await user_manager.check_rate_limit(free_user.user_id)
    print(f"✅ Rate limit check: {allowed}, limits: {limits}")
    
    # Simulate API usage
    for i in range(5):
        await user_manager.record_usage(
            free_user.user_id,
            "/analyze",
            0.5 + i * 0.1,
            tokens_used=100
        )
    
    # Get analytics
    analytics = await user_manager.get_usage_analytics(free_user.user_id)
    print(f"✅ Usage analytics: {analytics}")
    
    print("\n🎯 User Management System Ready!")

if __name__ == "__main__":
    asyncio.run(demo_user_management())
