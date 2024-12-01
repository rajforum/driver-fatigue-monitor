import logging
from typing import Optional
from app.services.trends import TrendService
from app.services.alerts import AlertService
from app.services.metrics import MetricsService
from app.services.websocket import SocketService

logger = logging.getLogger(__name__)

class ServiceManager:
    _instance: Optional['ServiceManager'] = None
    
    def __init__(self):
        self.trend_service = None
        self.alert_service = None
        self.metric_service = None
        self.socket_service = None
        self.initialized = False

    @classmethod
    def get_instance(cls) -> 'ServiceManager':
        if cls._instance is None:
            cls._instance = ServiceManager()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance"""
        if cls._instance is not None:
            cls._instance.cleanup()
            cls._instance = None

    def initialize(self, app):
        """Initialize all services with the app context"""
        if self.initialized:
            logger.warning("Services already initialized")
            return

        try:
            logger.info("Initializing services...")
            
            # Initialize services in order of dependency
            self.alert_service = AlertService()
            self.metric_service = MetricsService()
            self.trend_service = TrendService()
            self.socket_service = SocketService()
            
            # Initialize socket service with app
            self.socket_service.init_app(app)
            
            self.initialized = True
            logger.info("Services initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing services: {str(e)}")
            raise

    @property
    def trends(self) -> TrendService:
        if not self.initialized:
            raise RuntimeError("Services not initialized")
        return self.trend_service

    @property
    def alerts(self) -> AlertService:
        if not self.initialized:
            raise RuntimeError("Services not initialized")
        return self.alert_service

    @property
    def metrics(self) -> MetricsService:
        if not self.initialized:
            raise RuntimeError("Services not initialized")
        return self.metric_service

    @property
    def sockets(self) -> SocketService:
        if not self.initialized:
            raise RuntimeError("Services not initialized")
        return self.socket_service

    def cleanup(self):
        """Clean up all services and resources"""
        if not self.initialized:
            logger.warning("Services not initialized, nothing to clean up")
            return

        try:
            logger.info("Starting service cleanup...")
            
            # Cleanup in reverse order of initialization
            if self.socket_service:
                self.socket_service.cleanup()
                self.socket_service = None
            
            if self.trend_service:
                self.trend_service.cleanup()
                self.trend_service = None
            
            if self.metric_service:
                self.metric_service.cleanup()
                self.metric_service = None
            
            if self.alert_service:
                self.alert_service.cleanup()
                self.alert_service = None

            self.initialized = False
            # Reset the singleton instance
            ServiceManager.reset_instance()
            logger.info("Services cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during service cleanup: {str(e)}")
            raise

    def shutdown(self):
        """Graceful shutdown of all services"""
        try:
            logger.info("Starting service shutdown...")
            
            # Save any pending data before shutdown
            if self.trend_service:
                self.trend_service.save_pending_data()
            
            # Disconnect clients and stop real-time updates
            if self.socket_service:
                self.socket_service.shutdown()
            
            # Stop monitoring and background tasks
            if self.metric_service:
                self.metric_service.stop_monitoring()
            
            # Clean up all resources and reset singleton
            self.cleanup()
            
            logger.info("Services shut down successfully")
        except Exception as e:
            logger.error(f"Error during service shutdown: {str(e)}")
            raise 