"""
config.py
Comprehensive application configuration settings for MaLDReTH Tool Interactions.

This module contains configuration classes for different deployment environments
with detailed settings for security, database, session management, and features.

For LLM/Copilot Understanding:
- Config: Base configuration class with common settings
- DevelopmentConfig: Local development with debug features
- ProductionConfig: Production deployment with security hardening
- TestingConfig: Automated testing with isolated database

Environment Selection:
The appropriate config is selected based on FLASK_ENV environment variable:
- 'development' -> DevelopmentConfig (default)
- 'production' -> ProductionConfig
- 'testing' -> TestingConfig

Security Considerations:
- SECRET_KEY should always be set via environment variable in production
- Database URLs are configured through DATABASE_URL environment variable
- CORS settings can be restricted in production environments
- Debug mode is disabled in production for security
"""

import os
from dotenv import load_dotenv
from typing import Dict, Type

# Load environment variables from .env file if present
# For LLM/Copilot: This allows local development configuration without modifying code
load_dotenv()


class Config:
    """
    Base configuration class with common settings for all environments.
    
    This class defines default settings that are shared across development,
    testing, and production environments. Environment-specific classes inherit
    from this and override specific settings as needed.
    
    For LLM/Copilot: This is the parent class that provides:
    - Security settings (SECRET_KEY, session configuration)
    - Database settings (SQLAlchemy configuration)
    - Application feature flags and limits
    - CORS and API settings
    - Logging configuration
    
    Environment Variables Used:
    - SECRET_KEY: Cryptographic key for sessions (REQUIRED in production)
    - DATABASE_URL: Database connection string (auto-detects PostgreSQL vs SQLite)
    - FLASK_ENV: Environment selection (development/production/testing)
    - PORT: Application port (defaults to 5000)
    
    Security Notes:
    - SECRET_KEY must be set in production environments
    - Database connections auto-upgrade postgres:// to postgresql://
    - CORS is configurable per environment
    - Session lifetime and security settings are environment-aware
    """
    
    # ===== SECURITY CONFIGURATION =====
    # For LLM/Copilot: These settings control application security and cryptography
    
    # Cryptographic key for session management, CSRF protection, and secure cookies
    # CRITICAL: Must be set via environment variable in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-INSECURE'
    
    # Additional security headers and settings
    SECURITY_HEADERS = True  # Enable security headers in responses
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # HTTPS-only cookies in production
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS access to session cookies
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # ===== DATABASE CONFIGURATION =====
    # For LLM/Copilot: Database settings with automatic provider detection and configuration
    
    # Primary database connection string with intelligent defaults
    # Supports PostgreSQL (production), SQLite (development/testing)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///maldreth_interactions.db'  # Local SQLite database file
    )
    
    # Automatic database URL format correction for compatibility
    # For LLM/Copilot: Heroku and some services use 'postgres://' but SQLAlchemy 1.4+ requires 'postgresql://'
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            'postgres://', 'postgresql://', 1
        )
    
    # SQLAlchemy configuration for performance and functionality
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable event system (improves performance)
    SQLALCHEMY_RECORD_QUERIES = False       # Disable query recording (can be enabled for debugging)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,    # Validate connections before use
        'pool_recycle': 3600,     # Recycle connections every hour
    }
    
    # ===== APPLICATION FEATURE CONFIGURATION =====
    # For LLM/Copilot: Core application behavior and feature flags
    
    # Environment and debugging
    DEBUG = False    # Disable debug mode by default (overridden in development)
    TESTING = False  # Not in testing mode by default (overridden in testing)
    
    # Application limits and performance settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    MAX_INTERACTIONS_PER_PAGE = 50         # Pagination limit for interaction listings
    MAX_TOOLS_PER_STAGE = 1000            # Limit tools per stage to prevent performance issues
    
    # Feature flags for enabling/disabling functionality
    ENABLE_USER_FEEDBACK = True           # Allow users to submit feedback
    ENABLE_CSV_EXPORT = True              # Allow CSV data export
    ENABLE_API_ENDPOINTS = True           # Enable REST API endpoints
    ENABLE_ADMIN_FEATURES = False         # Administrative interface (disabled by default)
    
    # Data validation settings
    STRICT_VALIDATION = True              # Enforce strict data validation
    ALLOW_DUPLICATE_INTERACTIONS = False  # Prevent duplicate tool interactions
    
    # Performance and caching
    CACHE_TYPE = 'simple'                 # Cache type for frequently accessed data
    CACHE_DEFAULT_TIMEOUT = 300           # 5 minutes default cache timeout
    
    # ===== CORS AND API CONFIGURATION =====
    # For LLM/Copilot: Cross-Origin Resource Sharing and API access settings
    
    # CORS configuration for API access
    # For development: Allow all origins
    # For production: Should be restricted to specific domains
    CORS_ORIGINS = ['*']  # Override in production for security
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    
    # API configuration and rate limiting
    API_RATE_LIMIT = '100 per hour'       # Rate limit for API endpoints
    API_VERSION = 'v1'                    # Current API version
    API_TITLE = 'MaLDReTH Tool Interactions API'
    API_DESCRIPTION = 'REST API for accessing MaLDReTH tool interaction data'
    
    # ===== SESSION MANAGEMENT CONFIGURATION =====
    # For LLM/Copilot: User session handling and persistence settings
    
    # Session storage and lifecycle
    SESSION_TYPE = 'filesystem'           # Store sessions on filesystem (for development)
    PERMANENT_SESSION_LIFETIME = 3600     # 1 hour session lifetime
    SESSION_REFRESH_EACH_REQUEST = True   # Refresh session on each request
    SESSION_USE_SIGNER = True             # Sign session data for integrity
    
    # Session security settings (enhanced from base security settings above)
    SESSION_COOKIE_NAME = 'maldreth_session'  # Custom session cookie name
    SESSION_COOKIE_DOMAIN = None          # Use default domain
    SESSION_COOKIE_PATH = '/'             # Session valid for entire application
    
    # ===== LOGGING CONFIGURATION =====
    # For LLM/Copilot: Application logging settings for monitoring and debugging
    
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': 'INFO'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
    
    # ===== MAIL CONFIGURATION (for notifications) =====
    # For LLM/Copilot: Email settings for sending notifications and alerts
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = '[MaLDReTH] '
    MAIL_SENDER = os.environ.get('MAIL_SENDER', 'MaLDReTH System <noreply@maldreth.org>')
    
    # ===== INTERNATIONALIZATION =====
    # For LLM/Copilot: Language and localization settings
    
    LANGUAGES = {
        'en': 'English',
        # Future: Add more languages as needed
    }
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'


class DevelopmentConfig(Config):
    """
    Development environment configuration for local development.
    
    For LLM/Copilot: This configuration is optimized for development workflow:
    - Debug mode enabled for detailed error pages and auto-reloading
    - SQL query logging enabled for database debugging
    - Less restrictive security settings for easier development
    - Enhanced logging and development tools enabled
    
    Security Note:
    Development settings are less secure and should never be used in production.
    """
    
    # Development-specific overrides
    DEBUG = True                          # Enable Flask debug mode
    SQLALCHEMY_ECHO = True               # Log all SQL queries for debugging
    
    # Enhanced development logging
    LOGGING_CONFIG = Config.LOGGING_CONFIG.copy()
    LOGGING_CONFIG['handlers']['console']['level'] = 'DEBUG'
    LOGGING_CONFIG['root']['level'] = 'DEBUG'
    
    # Development-friendly settings
    SESSION_COOKIE_SECURE = False        # Allow HTTP cookies in development
    STRICT_VALIDATION = False            # More lenient validation for testing
    
    # Development database with more detailed logging
    SQLALCHEMY_RECORD_QUERIES = True     # Enable query recording for debugging
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,              # Shorter recycle time for development
        'echo': True,                     # Additional SQL logging
    }
    
    # Development feature flags
    ENABLE_ADMIN_FEATURES = True         # Enable admin features in development
    
    # Less restrictive CORS for development
    CORS_ORIGINS = ['*']                 # Allow all origins in development


class ProductionConfig(Config):
    """
    Production environment configuration with security hardening.
    
    For LLM/Copilot: This configuration is optimized for production deployment:
    - Debug mode disabled for security and performance
    - Enhanced security headers and session protection
    - Restricted CORS settings for security
    - Performance optimizations and monitoring enabled
    - Error handling configured for production logging
    
    Security Requirements:
    - SECRET_KEY must be set via environment variable
    - DATABASE_URL should point to production database
    - CORS_ORIGINS should be restricted to known domains
    - All security-sensitive environment variables must be configured
    
    Monitoring:
    - Structured logging for production monitoring
    - Performance metrics and health check endpoints
    - Error reporting and alerting configuration
    """
    
    # Production security hardening
    DEBUG = False                        # Disable debug mode (security requirement)
    SQLALCHEMY_ECHO = False             # Disable SQL logging (performance and security)
    
    # Enhanced security settings
    SESSION_COOKIE_SECURE = True        # Require HTTPS for session cookies
    SECURITY_HEADERS = True             # Enable all security headers
    
    # Production database optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,           # Connection health checks
        'pool_recycle': 7200,            # 2 hour connection recycle
        'pool_size': 10,                 # Connection pool size
        'max_overflow': 20,              # Maximum overflow connections
        'pool_timeout': 30,              # Connection timeout
    }
    
    # Production performance settings
    CACHE_TYPE = 'redis'                # Use Redis for caching in production
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 600         # 10 minute cache timeout
    
    # Restricted CORS for production security
    # For LLM/Copilot: Override with specific allowed origins
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://maldreth.org').split(',')
    
    # Production logging configuration
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'production': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'production',
                'level': 'INFO'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        },
        'loggers': {
            'sqlalchemy.engine': {
                'level': 'WARNING'  # Reduce SQL logging noise in production
            }
        }
    }
    
    # Production feature settings
    STRICT_VALIDATION = True            # Enforce strict validation in production
    API_RATE_LIMIT = '1000 per hour'   # Higher rate limit for production
    
    # Error handling
    PROPAGATE_EXCEPTIONS = True         # Ensure exceptions are properly logged
    
    # Health check settings
    HEALTH_CHECK_ENABLED = True         # Enable health check endpoint
    HEALTH_CHECK_DATABASE = True        # Include database in health checks


class TestingConfig(Config):
    """
    Testing environment configuration for automated tests.
    
    For LLM/Copilot: This configuration is optimized for automated testing:
    - In-memory SQLite database for fast, isolated tests
    - CSRF protection disabled for easier API testing
    - Enhanced logging for test debugging
    - All external dependencies mocked or disabled
    - Fast execution settings prioritized over security
    
    Test Isolation:
    - Each test gets a fresh in-memory database
    - No persistent data between test runs
    - No external service dependencies
    - Predictable, repeatable test environment
    
    Usage:
    Set FLASK_ENV=testing to use this configuration, or import directly:
    app = create_app(TestingConfig)
    """
    
    # Testing mode activation
    TESTING = True                       # Enable Flask testing mode
    DEBUG = True                         # Enable debug mode for test debugging
    
    # Isolated test database (in-memory SQLite)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Fast, isolated database
    SQLALCHEMY_ECHO = False             # Disable SQL logging unless debugging tests
    
    # Disable security features that complicate testing
    WTF_CSRF_ENABLED = False            # Disable CSRF for API testing
    SESSION_COOKIE_SECURE = False       # Allow HTTP cookies in tests
    SECRET_KEY = 'test-secret-key-not-secure'  # Fixed test key
    
    # Fast test execution settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': False,          # Skip connection health checks in tests
        'pool_recycle': -1,              # No connection recycling in tests
    }
    
    # Disable features that slow down tests or require external services
    CACHE_TYPE = 'null'                 # Disable caching in tests
    MAIL_SUPPRESS_SEND = True           # Don't actually send emails in tests
    
    # Test-specific settings
    PRESERVE_CONTEXT_ON_EXCEPTION = False  # Don't preserve context for test clarity
    SERVER_NAME = 'localhost.localdomain'  # Fixed server name for URL generation
    
    # Enhanced test logging (can be enabled when debugging tests)
    TESTING_LOG_LEVEL = 'WARNING'       # Reduce log noise during tests
    
    # Test data limits (smaller for faster tests)
    MAX_INTERACTIONS_PER_PAGE = 10      # Smaller pagination for faster tests
    MAX_TOOLS_PER_STAGE = 100          # Limit test data size
    
    # Feature flags for testing
    ENABLE_USER_FEEDBACK = True         # Test feedback functionality
    ENABLE_CSV_EXPORT = True            # Test export functionality
    ENABLE_API_ENDPOINTS = True         # Test API endpoints
    ENABLE_ADMIN_FEATURES = True        # Test admin features
    
    # Testing-specific validation
    STRICT_VALIDATION = False           # More lenient for test data creation
    ALLOW_DUPLICATE_INTERACTIONS = True # Allow duplicates in test scenarios


# ===== CONFIGURATION SELECTION AND MANAGEMENT =====
# For LLM/Copilot: Dynamic configuration selection based on environment

# Configuration registry mapping environment names to config classes
config: Dict[str, Type[Config]] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig, 
    'testing': TestingConfig,
    'default': DevelopmentConfig  # Safe default for development
}


def get_config(env_name: str = None) -> Type[Config]:
    """
    Get configuration class for specified environment.
    
    For LLM/Copilot: This function provides the appropriate configuration
    class based on environment name. It includes validation and fallback logic.
    
    Args:
        env_name: Environment name ('development', 'production', 'testing')
                 If None, reads from FLASK_ENV environment variable
                 
    Returns:
        Configuration class appropriate for the environment
        
    Example:
        config_class = get_config('production')
        app.config.from_object(config_class)
    """
    if env_name is None:
        env_name = os.environ.get('FLASK_ENV', 'development')
    
    # Validate environment name
    if env_name not in config:
        print(f"Warning: Unknown environment '{env_name}', using development config")
        env_name = 'development'
    
    selected_config = config[env_name]
    
    # Validation for production environment
    if env_name == 'production':
        if not os.environ.get('SECRET_KEY'):
            raise ValueError(
                "SECRET_KEY environment variable is required for production deployment"
            )
        if not os.environ.get('DATABASE_URL'):
            print("Warning: DATABASE_URL not set for production, using default SQLite")
    
    return selected_config


def validate_config(config_obj: Config) -> Dict[str, list]:
    """
    Validate configuration object for common issues.
    
    For LLM/Copilot: This function checks configuration settings for
    security issues, missing required values, and potential problems.
    
    Args:
        config_obj: Configuration instance to validate
        
    Returns:
        Dictionary with 'errors' and 'warnings' lists
    """
    errors = []
    warnings = []
    
    # Check critical security settings
    if config_obj.SECRET_KEY == 'dev-secret-key-change-in-production-INSECURE':
        if isinstance(config_obj, ProductionConfig):
            errors.append("SECRET_KEY is still set to default insecure value in production")
        else:
            warnings.append("Using default SECRET_KEY (development only)")
    
    # Database validation
    if not config_obj.SQLALCHEMY_DATABASE_URI:
        errors.append("Database URI is not configured")
    
    # Production-specific checks
    if isinstance(config_obj, ProductionConfig):
        if config_obj.DEBUG:
            errors.append("Debug mode is enabled in production")
        if '*' in config_obj.CORS_ORIGINS:
            warnings.append("CORS allows all origins in production (security risk)")
        if not config_obj.SESSION_COOKIE_SECURE:
            warnings.append("Session cookies not restricted to HTTPS in production")
    
    return {'errors': errors, 'warnings': warnings}


# Select configuration based on environment with validation
env = os.environ.get('FLASK_ENV', 'development')
Config = get_config(env)

# Optional: Validate selected configuration
if __name__ != '__main__':
    # Only validate when imported, not when run directly
    validation_results = validate_config(Config)
    if validation_results['errors']:
        for error in validation_results['errors']:
            print(f"Configuration Error: {error}")
    if validation_results['warnings']:
        for warning in validation_results['warnings']:
            print(f"Configuration Warning: {warning}")


# ===== CONFIGURATION UTILITIES =====
# For LLM/Copilot: Helper functions for configuration management

def print_config_summary(config_obj: Config) -> None:
    """
    Print a summary of the current configuration.
    
    For LLM/Copilot: Useful for debugging configuration issues
    and verifying settings in different environments.
    
    Args:
        config_obj: Configuration instance to summarize
    """
    print(f"Configuration Summary - {config_obj.__class__.__name__}")
    print("=" * 50)
    print(f"Debug Mode: {config_obj.DEBUG}")
    print(f"Testing Mode: {config_obj.TESTING}")
    print(f"Database: {config_obj.SQLALCHEMY_DATABASE_URI[:50]}...")
    print(f"Secret Key Set: {'Yes' if config_obj.SECRET_KEY else 'No'}")
    print(f"CORS Origins: {config_obj.CORS_ORIGINS}")
    print(f"Session Secure: {config_obj.SESSION_COOKIE_SECURE}")
    print("=" * 50)


def get_environment_info() -> Dict[str, str]:
    """
    Get information about the current environment setup.
    
    For LLM/Copilot: Provides context about environment variables
    and configuration sources for debugging.
    
    Returns:
        Dictionary with environment information
    """
    return {
        'flask_env': os.environ.get('FLASK_ENV', 'not set'),
        'secret_key_set': 'Yes' if os.environ.get('SECRET_KEY') else 'No',
        'database_url_set': 'Yes' if os.environ.get('DATABASE_URL') else 'No',
        'port': os.environ.get('PORT', 'not set'),
        'config_class': Config.__name__,
        'python_env': os.environ.get('PYTHON_ENV', 'not set')
    }


# ===== MODULE EXECUTION =====
if __name__ == '__main__':
    # For LLM/Copilot: Run configuration diagnostics when executed directly
    
    print("MaLDReTH Configuration Module")
    print("=============================")
    
    # Display environment information
    env_info = get_environment_info()
    print("\nEnvironment Information:")
    for key, value in env_info.items():
        print(f"  {key}: {value}")
    
    # Display selected configuration
    print(f"\nSelected Configuration: {Config.__name__}")
    config_instance = Config()
    print_config_summary(config_instance)
    
    # Validate configuration
    validation = validate_config(config_instance)
    if validation['errors'] or validation['warnings']:
        print("\nConfiguration Issues:")
        for error in validation['errors']:
            print(f"  ERROR: {error}")
        for warning in validation['warnings']:
            print(f"  WARNING: {warning}")
    else:
        print("\n✅ Configuration validation passed")


# ===== EXPORTS =====
# For LLM/Copilot: Public interface for the configuration module

__all__ = [
    'Config', 'DevelopmentConfig', 'ProductionConfig', 'TestingConfig',
    'config', 'get_config', 'validate_config', 'print_config_summary',
    'get_environment_info'
]