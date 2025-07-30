"""
Logging Utilities

This module provides centralized logging configuration for the Smart Receipt Processor.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import os

def setup_logger(
    name: Optional[str] = None,
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup and configure logger for the application.
    
    Args:
        name: Logger name (defaults to root logger)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    
    # Get logger
    logger = logging.getLogger(name)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Failed to setup file logging: {e}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the application's standard configuration.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def configure_third_party_loggers():
    """Configure logging levels for third-party libraries."""
    
    # Reduce noise from common libraries
    third_party_loggers = {
        'urllib3': logging.WARNING,
        'requests': logging.WARNING,
        'PIL': logging.WARNING,
        'matplotlib': logging.WARNING,
        'openai': logging.WARNING,
        'httpx': logging.WARNING
    }
    
    for logger_name, level in third_party_loggers.items():
        logging.getLogger(logger_name).setLevel(level)

def log_system_info(logger: logging.Logger):
    """Log system information for debugging purposes."""
    import platform
    import sys
    
    logger.info("=== System Information ===")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Architecture: {platform.architecture()}")
    logger.info(f"Processor: {platform.processor()}")
    
    # Log available packages
    try:
        import pkg_resources
        installed_packages = [d.project_name for d in pkg_resources.working_set]
        key_packages = ['openai', 'pillow', 'pytesseract', 'opencv-python', 'pandas', 'openpyxl']
        
        logger.info("=== Key Package Versions ===")
        for package in key_packages:
            if package in installed_packages:
                try:
                    version = pkg_resources.get_distribution(package).version
                    logger.info(f"{package}: {version}")
                except:
                    logger.info(f"{package}: installed (version unknown)")
            else:
                logger.warning(f"{package}: not installed")
                
    except ImportError:
        logger.warning("pkg_resources not available for package version checking")

def log_configuration(logger: logging.Logger, config):
    """Log configuration details (excluding sensitive information)."""
    logger.info("=== Configuration ===")
    
    config_dict = config.to_dict() if hasattr(config, 'to_dict') else vars(config)
    
    for key, value in config_dict.items():
        # Skip sensitive keys
        if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'token', 'password']):
            logger.info(f"{key}: [REDACTED]")
        else:
            logger.info(f"{key}: {value}")

def setup_application_logging(log_level: str = "INFO", log_dir: Optional[str] = None) -> logging.Logger:
    """
    Setup comprehensive logging for the entire application.
    
    Args:
        log_level: Logging level
        log_dir: Directory for log files (optional)
        
    Returns:
        Main application logger
    """
    
    # Determine log file path
    log_file = None
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        log_file = str(log_path / "smart_receipt_processor.log")
    
    # Setup main logger
    main_logger = setup_logger(
        name="smart_receipt_processor",
        level=log_level,
        log_file=log_file
    )
    
    # Configure third-party loggers
    configure_third_party_loggers()
    
    # Log startup information
    main_logger.info("Smart Receipt Processor logging initialized")
    log_system_info(main_logger)
    
    return main_logger

class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return logging.getLogger(f"{self.__module__}.{self.__class__.__name__}")

def log_function_call(func):
    """Decorator to log function calls with arguments and timing."""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        # Log function entry
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {str(e)}")
            raise
    
    return wrapper

def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """
    Log exception with full traceback and context.
    
    Args:
        logger: Logger instance
        exception: Exception to log
        context: Additional context information
    """
    import traceback
    
    error_msg = f"Exception occurred"
    if context:
        error_msg += f" in {context}"
    error_msg += f": {str(exception)}"
    
    logger.error(error_msg)
    logger.debug(f"Full traceback:\n{traceback.format_exc()}")

# Global logger instance for convenience
app_logger = logging.getLogger("smart_receipt_processor")
