"""
System diagnostics and monitoring utilities for BHV application.

This module provides comprehensive system health checks, performance monitoring,
and troubleshooting tools for healthcare deployment environments.
"""

import os
import sys
import psutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import traceback

from config.settings import Config
from models.database import get_db_connection, DatabaseManager


class DiagnosticsManager:
    """
    Comprehensive system diagnostics and health monitoring.
    
    Provides system health checks, performance metrics, database diagnostics,
    and troubleshooting information for BHV deployment.
    """
    
    def __init__(self):
        """Initialize diagnostics manager with configuration."""
        self.config = Config()
        self.db_manager = DatabaseManager()
        self.start_time = datetime.utcnow()
    
    def run_full_diagnostics(self) -> Dict[str, Any]:
        """
        Run comprehensive system diagnostics.
        
        Returns:
            Dict[str, Any]: Complete diagnostic results
        """
        diagnostics = {
            'timestamp': datetime.utcnow().isoformat(),
            'system_info': self.get_system_info(),
            'application_health': self.check_application_health(),
            'database_health': self.check_database_health(),
            'file_system_health': self.check_file_system_health(),
            'security_status': self.check_security_status(),
            'performance_metrics': self.get_performance_metrics(),
            'configuration_status': self.validate_configuration(),
            'recent_errors': self.get_recent_errors(),
            'recommendations': self.generate_recommendations()
        }
        
        # Calculate overall health score
        diagnostics['overall_health'] = self.calculate_health_score(diagnostics)
        
        return diagnostics
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get basic system information.
        
        Returns:
            Dict[str, Any]: System information
        """
        try:
            return {
                'platform': sys.platform,
                'python_version': sys.version,
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'disk_usage': self.get_disk_usage(),
                'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
                'process_id': os.getpid(),
                'working_directory': os.getcwd()
            }
        except Exception as e:
            return {'error': f'Failed to get system info: {str(e)}'}
    
    def check_application_health(self) -> Dict[str, Any]:
        """
        Check application-specific health metrics.
        
        Returns:
            Dict[str, Any]: Application health status
        """
        health = {
            'status': 'healthy',
            'checks': {},
            'issues': []
        }
        
        try:
            # Check if Flask app is running
            health['checks']['flask_running'] = True
            
            # Check configuration loading
            try:
                config_valid = self.config.validate_config()
                health['checks']['configuration'] = all(config_valid.values())
                if not health['checks']['configuration']:
                    health['issues'].append('Configuration validation failed')
            except Exception as e:
                health['checks']['configuration'] = False
                health['issues'].append(f'Configuration error: {str(e)}')
            
            # Check required directories
            required_dirs = [
                self.config.UPLOAD_FOLDER,
                Path(self.config.DATABASE_PATH).parent,
                Path(self.config.LOG_FILE).parent
            ]
            
            dirs_ok = True
            for directory in required_dirs:
                if not Path(directory).exists():
                    dirs_ok = False
                    health['issues'].append(f'Missing directory: {directory}')
            
            health['checks']['directories'] = dirs_ok
            
            # Check memory usage
            memory_percent = psutil.virtual_memory().percent
            health['checks']['memory_usage'] = memory_percent < 90
            if memory_percent >= 90:
                health['issues'].append(f'High memory usage: {memory_percent}%')
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            health['checks']['cpu_usage'] = cpu_percent < 80
            if cpu_percent >= 80:
                health['issues'].append(f'High CPU usage: {cpu_percent}%')
            
            # Determine overall status
            if health['issues']:
                health['status'] = 'degraded' if len(health['issues']) < 3 else 'unhealthy'
            
        except Exception as e:
            health['status'] = 'error'
            health['error'] = str(e)
        
        return health
    
    def check_database_health(self) -> Dict[str, Any]:
        """
        Check database connectivity and health.
        
        Returns:
            Dict[str, Any]: Database health status
        """
        health = {
            'status': 'healthy',
            'checks': {},
            'statistics': {},
            'issues': []
        }
        
        try:
            # Test database connection
            conn = get_db_connection()
            health['checks']['connectivity'] = True
            
            # Check database file exists and is readable
            db_path = Path(self.config.DATABASE_PATH)
            health['checks']['file_exists'] = db_path.exists()
            health['checks']['file_readable'] = db_path.is_file() and os.access(db_path, os.R_OK)
            
            # Get database statistics
            health['statistics'] = self.db_manager.get_database_stats()
            
            # Check table integrity
            tables = ['users', 'images', 'narratives', 'audit_log', 'user_sessions']
            tables_ok = True
            
            for table in tables:
                try:
                    conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()
                except sqlite3.Error:
                    tables_ok = False
                    health['issues'].append(f'Table {table} is corrupted or missing')
            
            health['checks']['table_integrity'] = tables_ok
            
            # Check for database locks
            try:
                conn.execute('BEGIN IMMEDIATE').fetchone()
                conn.rollback()
                health['checks']['no_locks'] = True
            except sqlite3.OperationalError:
                health['checks']['no_locks'] = False
                health['issues'].append('Database is locked')
            
            # Check database size
            db_size_mb = health['statistics'].get('database_size_mb', 0)
            health['checks']['size_reasonable'] = db_size_mb < 1000  # Less than 1GB
            if db_size_mb >= 1000:
                health['issues'].append(f'Large database size: {db_size_mb:.1f}MB')
            
            conn.close()
            
            # Determine overall status
            if health['issues']:
                health['status'] = 'degraded' if len(health['issues']) < 2 else 'unhealthy'
            
        except Exception as e:
            health['status'] = 'error'
            health['error'] = str(e)
            health['checks']['connectivity'] = False
        
        return health
    
    def check_file_system_health(self) -> Dict[str, Any]:
        """
        Check file system health and storage status.
        
        Returns:
            Dict[str, Any]: File system health status
        """
        health = {
            'status': 'healthy',
            'checks': {},
            'storage_info': {},
            'issues': []
        }
        
        try:
            # Check upload directory
            upload_dir = Path(self.config.UPLOAD_FOLDER)
            health['checks']['upload_dir_exists'] = upload_dir.exists()
            health['checks']['upload_dir_writable'] = upload_dir.exists() and os.access(upload_dir, os.W_OK)
            
            if not health['checks']['upload_dir_exists']:
                health['issues'].append('Upload directory does not exist')
            elif not health['checks']['upload_dir_writable']:
                health['issues'].append('Upload directory is not writable')
            
            # Check disk space
            disk_usage = psutil.disk_usage(upload_dir.parent if upload_dir.exists() else '.')
            free_space_gb = disk_usage.free / (1024**3)
            total_space_gb = disk_usage.total / (1024**3)
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            health['storage_info'] = {
                'total_gb': round(total_space_gb, 2),
                'free_gb': round(free_space_gb, 2),
                'used_percent': round(used_percent, 1)
            }
            
            health['checks']['sufficient_space'] = free_space_gb > 1.0  # At least 1GB free
            health['checks']['not_full'] = used_percent < 95
            
            if free_space_gb <= 1.0:
                health['issues'].append(f'Low disk space: {free_space_gb:.1f}GB free')
            
            if used_percent >= 95:
                health['issues'].append(f'Disk nearly full: {used_percent:.1f}% used')
            
            # Check file permissions
            test_file = upload_dir / '.bhv_test'
            try:
                test_file.touch()
                test_file.unlink()
                health['checks']['file_operations'] = True
            except Exception:
                health['checks']['file_operations'] = False
                health['issues'].append('Cannot create/delete files in upload directory')
            
            # Determine overall status
            if health['issues']:
                health['status'] = 'degraded' if len(health['issues']) < 2 else 'unhealthy'
            
        except Exception as e:
            health['status'] = 'error'
            health['error'] = str(e)
        
        return health
    
    def check_security_status(self) -> Dict[str, Any]:
        """
        Check security configuration and status.
        
        Returns:
            Dict[str, Any]: Security status
        """
        security = {
            'status': 'secure',
            'checks': {},
            'warnings': []
        }
        
        try:
            # Check secret key strength
            secret_key_secure = len(self.config.SECRET_KEY) >= 32
            security['checks']['secret_key_secure'] = secret_key_secure
            if not secret_key_secure:
                security['warnings'].append('Weak secret key detected')
            
            # Check debug mode
            debug_disabled = not self.config.DEBUG
            security['checks']['debug_disabled'] = debug_disabled
            if not debug_disabled:
                security['warnings'].append('Debug mode is enabled in production')
            
            # Check file upload restrictions
            security['checks']['file_upload_restricted'] = bool(self.config.ALLOWED_EXTENSIONS)
            security['checks']['file_size_limited'] = self.config.MAX_CONTENT_LENGTH < 50 * 1024 * 1024  # 50MB
            
            # Check audit logging
            security['checks']['audit_enabled'] = self.config.AUDIT_ENABLED
            if not self.config.AUDIT_ENABLED:
                security['warnings'].append('Audit logging is disabled')
            
            # Check session configuration
            security['checks']['session_timeout_set'] = self.config.SESSION_TIMEOUT < 7200  # 2 hours max
            
            # Determine overall status
            if security['warnings']:
                security['status'] = 'warning' if len(security['warnings']) < 3 else 'insecure'
            
        except Exception as e:
            security['status'] = 'error'
            security['error'] = str(e)
        
        return security
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics.
        
        Returns:
            Dict[str, Any]: Performance metrics
        """
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'disk_io': dict(psutil.disk_io_counters()._asdict()) if psutil.disk_io_counters() else {},
                'network_io': dict(psutil.net_io_counters()._asdict()) if psutil.net_io_counters() else {},
                'process_count': len(psutil.pids()),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        except Exception as e:
            return {'error': f'Failed to get performance metrics: {str(e)}'}
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate current configuration settings.
        
        Returns:
            Dict[str, Any]: Configuration validation results
        """
        try:
            validation = self.config.validate_config()
            
            return {
                'status': 'valid' if all(validation.values()) else 'invalid',
                'checks': validation,
                'config_summary': str(self.config)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_recent_errors(self) -> List[Dict[str, Any]]:
        """
        Get recent error logs and exceptions.
        
        Returns:
            List[Dict[str, Any]]: Recent error entries
        """
        errors = []
        
        try:
            log_file = Path(self.config.LOG_FILE)
            if log_file.exists():
                # Read last 100 lines of log file
                with open(log_file, 'r') as f:
                    lines = f.readlines()[-100:]
                
                for line in lines:
                    if 'ERROR' in line or 'CRITICAL' in line:
                        errors.append({
                            'timestamp': line.split()[0] if line.split() else 'unknown',
                            'level': 'ERROR' if 'ERROR' in line else 'CRITICAL',
                            'message': line.strip()
                        })
            
            # Limit to last 10 errors
            return errors[-10:]
            
        except Exception as e:
            return [{'error': f'Failed to read error logs: {str(e)}'}]
    
    def generate_recommendations(self) -> List[str]:
        """
        Generate system optimization and security recommendations.
        
        Returns:
            List[str]: List of recommendations
        """
        recommendations = []
        
        try:
            # Check system resources
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 80:
                recommendations.append('Consider increasing system memory or optimizing memory usage')
            
            # Check disk space
            disk_usage = psutil.disk_usage('.')
            free_space_gb = disk_usage.free / (1024**3)
            if free_space_gb < 5:
                recommendations.append('Low disk space - consider cleanup or adding storage')
            
            # Check configuration
            if self.config.DEBUG:
                recommendations.append('Disable debug mode for production deployment')
            
            if len(self.config.SECRET_KEY) < 32:
                recommendations.append('Use a stronger secret key (32+ characters)')
            
            # Check database
            try:
                db_stats = self.db_manager.get_database_stats()
                if db_stats.get('database_size_mb', 0) > 500:
                    recommendations.append('Consider database optimization or archiving old data')
            except Exception:
                pass
            
            # Security recommendations
            if not self.config.AUDIT_ENABLED:
                recommendations.append('Enable audit logging for compliance and security monitoring')
            
            if self.config.SESSION_TIMEOUT > 3600:
                recommendations.append('Consider shorter session timeout for better security')
            
        except Exception:
            recommendations.append('Unable to generate specific recommendations due to system error')
        
        return recommendations
    
    def calculate_health_score(self, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall system health score.
        
        Args:
            diagnostics (Dict[str, Any]): Full diagnostic results
            
        Returns:
            Dict[str, Any]: Health score and status
        """
        try:
            scores = []
            
            # Application health (30% weight)
            app_health = diagnostics.get('application_health', {})
            if app_health.get('status') == 'healthy':
                scores.append(100)
            elif app_health.get('status') == 'degraded':
                scores.append(70)
            else:
                scores.append(30)
            
            # Database health (25% weight)
            db_health = diagnostics.get('database_health', {})
            if db_health.get('status') == 'healthy':
                scores.append(100)
            elif db_health.get('status') == 'degraded':
                scores.append(60)
            else:
                scores.append(20)
            
            # File system health (20% weight)
            fs_health = diagnostics.get('file_system_health', {})
            if fs_health.get('status') == 'healthy':
                scores.append(100)
            elif fs_health.get('status') == 'degraded':
                scores.append(65)
            else:
                scores.append(25)
            
            # Security status (15% weight)
            security = diagnostics.get('security_status', {})
            if security.get('status') == 'secure':
                scores.append(100)
            elif security.get('status') == 'warning':
                scores.append(75)
            else:
                scores.append(40)
            
            # Configuration status (10% weight)
            config = diagnostics.get('configuration_status', {})
            if config.get('status') == 'valid':
                scores.append(100)
            else:
                scores.append(50)
            
            # Calculate weighted average
            weights = [0.3, 0.25, 0.2, 0.15, 0.1]
            overall_score = sum(score * weight for score, weight in zip(scores, weights))
            
            # Determine status
            if overall_score >= 90:
                status = 'excellent'
            elif overall_score >= 75:
                status = 'good'
            elif overall_score >= 60:
                status = 'fair'
            elif overall_score >= 40:
                status = 'poor'
            else:
                status = 'critical'
            
            return {
                'score': round(overall_score, 1),
                'status': status,
                'component_scores': {
                    'application': scores[0],
                    'database': scores[1],
                    'file_system': scores[2],
                    'security': scores[3],
                    'configuration': scores[4]
                }
            }
            
        except Exception as e:
            return {
                'score': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def get_disk_usage(self) -> Dict[str, float]:
        """
        Get disk usage information for relevant paths.
        
        Returns:
            Dict[str, float]: Disk usage percentages
        """
        usage = {}
        
        paths_to_check = [
            ('root', '.'),
            ('upload_folder', self.config.UPLOAD_FOLDER),
            ('database', str(Path(self.config.DATABASE_PATH).parent))
        ]
        
        for name, path in paths_to_check:
            try:
                if Path(path).exists():
                    disk_usage = psutil.disk_usage(path)
                    usage[name] = round((disk_usage.used / disk_usage.total) * 100, 1)
            except Exception:
                usage[name] = 0.0
        
        return usage