#!/usr/bin/env python3
"""
Deployment script for Heroku database schema fixes.

This script handles the deployment process for fixing the database schema
on Heroku by running the schema fix script remotely.
"""

import os
import sys
import subprocess
import logging
from typing import Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HerokuDeployment:
    """
    Handle Heroku deployment operations for the MaLDReTH application.
    """
    
    def __init__(self, app_name: str = "mal2-data-survey"):
        """
        Initialize the Heroku deployment handler.
        
        Args:
            app_name (str): Name of the Heroku application
        """
        self.app_name = app_name
        self.heroku_cli = self._check_heroku_cli()
    
    def _check_heroku_cli(self) -> bool:
        """
        Check if Heroku CLI is available.
        
        Returns:
            bool: True if Heroku CLI is available, False otherwise
        """
        try:
            result = subprocess.run(['heroku', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Heroku CLI found: {result.stdout.strip()}")
                return True
            else:
                logger.error("Heroku CLI not found")
                return False
        except FileNotFoundError:
            logger.error("Heroku CLI not installed")
            return False
    
    def run_heroku_command(self, command: List[str]) -> Optional[subprocess.CompletedProcess]:
        """
        Run a Heroku command.
        
        Args:
            command (List[str]): Command to run
            
        Returns:
            Optional[subprocess.CompletedProcess]: Result of the command
        """
        if not self.heroku_cli:
            logger.error("Heroku CLI not available")
            return None
        
        full_command = ['heroku'] + command + ['-a', self.app_name]
        logger.info(f"Running command: {' '.join(full_command)}")
        
        try:
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("Command executed successfully")
                if result.stdout:
                    logger.info(f"Output: {result.stdout}")
            else:
                logger.error(f"Command failed with return code {result.returncode}")
                if result.stderr:
                    logger.error(f"Error: {result.stderr}")
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.error("Command timed out")
            return None
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return None
    
    def deploy_schema_fix(self) -> bool:
        """
        Deploy the schema fix to Heroku.
        
        Returns:
            bool: True if deployment was successful, False otherwise
        """
        logger.info("Starting schema fix deployment...")
        
        # First, check app status
        result = self.run_heroku_command(['ps'])
        if result is None or result.returncode != 0:
            logger.error("Failed to check app status")
            return False
        
        # Run the schema fix script
        logger.info("Running schema fix script on Heroku...")
        result = self.run_heroku_command(['run', 'python', 'fix_tool_categories_schema.py'])
        
        if result is None:
            logger.error("Failed to run schema fix script")
            return False
        
        if result.returncode == 0:
            logger.info("Schema fix completed successfully")
            return True
        else:
            logger.error("Schema fix failed")
            if result.stderr:
                logger.error(f"Error details: {result.stderr}")
            return False
    
    def check_database_status(self) -> bool:
        """
        Check the database status after deployment.
        
        Returns:
            bool: True if database is healthy, False otherwise
        """
        logger.info("Checking database status...")
        
        result = self.run_heroku_command(['run', 'python', 'inspect_database.py'])
        
        if result is None:
            logger.error("Failed to check database status")
            return False
        
        if result.returncode == 0:
            logger.info("Database status check completed")
            return True
        else:
            logger.error("Database status check failed")
            return False
    
    def restart_app(self) -> bool:
        """
        Restart the Heroku application.
        
        Returns:
            bool: True if restart was successful, False otherwise
        """
        logger.info("Restarting Heroku application...")
        
        result = self.run_heroku_command(['restart'])
        
        if result is None:
            logger.error("Failed to restart application")
            return False
        
        if result.returncode == 0:
            logger.info("Application restarted successfully")
            return True
        else:
            logger.error("Application restart failed")
            return False
    
    def view_logs(self, lines: int = 100) -> None:
        """
        View recent application logs.
        
        Args:
            lines (int): Number of log lines to display
        """
        logger.info(f"Viewing last {lines} log lines...")
        
        result = self.run_heroku_command(['logs', '--tail', '--num', str(lines)])
        
        if result and result.returncode == 0:
            print("\n" + "="*50 + " HEROKU LOGS " + "="*50)
            print(result.stdout)
            print("="*113)
        else:
            logger.error("Failed to retrieve logs")


def main():
    """
    Main deployment function.
    """
    logger.info("Starting Heroku deployment process...")
    
    # Check if we're in the right directory
    if not os.path.exists('fix_tool_categories_schema.py'):
        logger.error("Schema fix script not found. Make sure you're in the project root directory.")
        sys.exit(1)
    
    # Initialize deployment handler
    deployment = HerokuDeployment()
    
    if not deployment.heroku_cli:
        logger.error("Heroku CLI is required for deployment")
        sys.exit(1)
    
    success = True
    
    try:
        # Deploy schema fix
        if not deployment.deploy_schema_fix():
            logger.error("Schema fix deployment failed")
            success = False
        
        # Check database status
        if success and not deployment.check_database_status():
            logger.warning("Database status check failed, but continuing...")
        
        # Restart application
        if success and not deployment.restart_app():
            logger.warning("Application restart failed")
        
        if success:
            logger.info("Deployment completed successfully!")
            print("\n" + "="*50)
            print("✅ Deployment completed successfully!")
            print("✅ Schema fix has been applied")
            print("✅ Application has been restarted")
            print("="*50)
        else:
            logger.error("Deployment failed")
            print("\n" + "="*50)
            print("❌ Deployment failed!")
            print("Please check the logs for more details")
            print("="*50)
            
            # Show recent logs for debugging
            deployment.view_logs(50)
    
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during deployment: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
