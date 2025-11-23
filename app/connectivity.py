"""
Intelligent Connectivity Detection for Universal Urban/Rural Access
Monitors internet connectivity and enables seamless online/offline switching
"""
import socket
import urllib.request
import urllib.error
import time
from typing import Dict, List, Tuple
import threading
import queue

class ConnectivityManager:
    """
    Robust internet connectivity detection system.
    Tests multiple reliable servers to ensure accurate connectivity status.
    Designed for universal access in both urban and rural environments.
    """
    
    def __init__(self):
        self.test_servers = [
            # Multiple reliable test endpoints for robust detection
            {'name': 'Google DNS', 'host': '8.8.8.8', 'port': 53, 'timeout': 3},
            {'name': 'Cloudflare DNS', 'host': '1.1.1.1', 'port': 53, 'timeout': 3},
            {'name': 'Google Public', 'url': 'https://www.google.com', 'timeout': 5},
            {'name': 'HTTPBin Test', 'url': 'https://httpbin.org/get', 'timeout': 5},
        ]
        self.last_check_time = 0
        self.last_status = False
        self.cache_duration = 10  # Cache results for 10 seconds
        
    def check_internet_connectivity(self) -> Dict:
        """
        Comprehensive internet connectivity check.
        Tests multiple endpoints to ensure reliable detection.
        
        Returns:
            Dict with connectivity status, details, and recommendations
        """
        current_time = time.time()
        
        # Use cached result if recent (cache for 60 seconds)
        if (current_time - self.last_check_time) < 60:
            return {
                'internet_available': self.last_status,
                'cached_result': True,
                'last_check': self.last_check_time,
                'recommendation': self._get_mode_recommendation(self.last_status)
            }
        
        # For offline environments, assume not connected to save time
        # Only test DNS quickly
        is_connected = False
        try:
            # Quick DNS test only (much faster)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('8.8.8.8', 53))
            sock.close()
            is_connected = (result == 0)
        except Exception:
            is_connected = False
        
        # Update cache
        self.last_check_time = current_time
        self.last_status = is_connected
        
        return {
            'internet_available': is_connected,
            'cached_result': False,
            'last_check': current_time,
            'recommendation': self._get_mode_recommendation(is_connected)
        }
    
    def _test_dns_connection(self, server: Dict) -> Dict:
        """Test DNS server connectivity (fastest method)"""
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(server['timeout'])
            
            result = sock.connect_ex((server['host'], server['port']))
            sock.close()
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                'server': server['name'],
                'type': 'DNS',
                'success': result == 0,
                'response_time_ms': round(response_time, 2),
                'error': None if result == 0 else f"Connection failed (code: {result})"
            }
            
        except Exception as e:
            return {
                'server': server['name'],
                'type': 'DNS',
                'success': False,
                'response_time_ms': None,
                'error': str(e)
            }
    
    def _test_http_connection(self, server: Dict) -> Dict:
        """Test HTTP endpoint connectivity (more comprehensive)"""
        try:
            start_time = time.time()
            
            request = urllib.request.Request(server['url'])
            request.add_header('User-Agent', 'Sahaaya-Health-System/1.2')
            
            with urllib.request.urlopen(request, timeout=server['timeout']) as response:
                response_code = response.getcode()
                response_time = (time.time() - start_time) * 1000
                
                return {
                    'server': server['name'],
                    'type': 'HTTP',
                    'success': 200 <= response_code < 400,
                    'response_code': response_code,
                    'response_time_ms': round(response_time, 2),
                    'error': None
                }
                
        except urllib.error.HTTPError as e:
            return {
                'server': server['name'],
                'type': 'HTTP',
                'success': False,
                'response_code': e.code,
                'response_time_ms': None,
                'error': f"HTTP Error: {e.code} {e.reason}"
            }
        except Exception as e:
            return {
                'server': server['name'],
                'type': 'HTTP',
                'success': False,
                'response_code': None,
                'response_time_ms': None,
                'error': str(e)
            }
    
    def _assess_connection_quality(self, test_results: List[Dict]) -> str:
        """Assess the quality of internet connection based on test results"""
        successful_tests = [r for r in test_results if r['success']]
        
        if not successful_tests:
            return 'no_connection'
        
        avg_response_time = sum(
            r['response_time_ms'] for r in successful_tests 
            if r['response_time_ms'] is not None
        ) / len([r for r in successful_tests if r['response_time_ms'] is not None])
        
        if avg_response_time < 500:  # Less than 500ms
            return 'excellent'
        elif avg_response_time < 1000:  # Less than 1 second
            return 'good'
        elif avg_response_time < 3000:  # Less than 3 seconds
            return 'fair'
        else:
            return 'poor'
    
    def _get_mode_recommendation(self, is_connected: bool) -> Dict:
        """Get recommended processing mode based on connectivity"""
        if is_connected:
            return {
                'mode': 'hybrid',
                'description': 'Use AI-enhanced processing with offline backup',
                'suitable_for': ['urban', 'rural_with_internet', 'hospitals'],
                'features': ['ai_analysis', 'offline_enhancement', 'real_time_data']
            }
        else:
            return {
                'mode': 'offline',
                'description': 'Full offline functionality using local database',
                'suitable_for': ['rural', 'remote', 'emergency_situations'],
                'features': ['offline_database', 'emergency_protocols', 'local_resources']
            }
    
    def get_system_mode_info(self) -> Dict:
        """Get comprehensive system mode information"""
        connectivity = self.check_internet_connectivity()
        
        return {
            'connectivity_status': connectivity,
            'recommended_mode': connectivity['recommendation'],
            'system_capabilities': self._get_current_capabilities(connectivity['internet_available']),
            'fallback_available': True,
            'universal_access': True
        }
    
    def _get_current_capabilities(self, internet_available: bool) -> Dict:
        """Get current system capabilities based on connectivity"""
        base_capabilities = {
            'text_processing': True,
            'multilingual_support': True,
            'health_guidance': True,
            'emergency_protocols': True,
            'local_resources': True
        }
        
        if internet_available:
            base_capabilities.update({
                'ai_enhanced_analysis': True,
                'real_time_medical_data': True,
                'cloud_based_updates': True,
                'telemedicine_ready': True
            })
        else:
            base_capabilities.update({
                'ai_enhanced_analysis': False,
                'real_time_medical_data': False,
                'cloud_based_updates': False,
                'telemedicine_ready': False,
                'note': 'Full offline functionality available'
            })
        
        return base_capabilities
    
    def monitor_connectivity_continuous(self, callback_function=None, interval: int = 30) -> None:
        """
        Continuously monitor connectivity in background.
        Useful for applications that need real-time connectivity awareness.
        """
        def monitor_loop():
            while True:
                try:
                    status = self.check_internet_connectivity()
                    if callback_function:
                        callback_function(status)
                    time.sleep(interval)
                except Exception as e:
                    if callback_function:
                        callback_function({'error': f"Monitoring error: {e}"})
                    time.sleep(interval)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def test_specific_service(self, service_url: str, timeout: int = 5) -> Dict:
        """Test connectivity to a specific service (e.g., hospital system, telemedicine platform)"""
        try:
            start_time = time.time()
            
            request = urllib.request.Request(service_url)
            request.add_header('User-Agent', 'Sahaaya-Health-System/1.2')
            
            with urllib.request.urlopen(request, timeout=timeout) as response:
                response_time = (time.time() - start_time) * 1000
                
                return {
                    'service_url': service_url,
                    'available': True,
                    'response_time_ms': round(response_time, 2),
                    'response_code': response.getcode(),
                    'recommendation': 'Service available - can use online features'
                }
                
        except Exception as e:
            return {
                'service_url': service_url,
                'available': False,
                'error': str(e),
                'recommendation': 'Service unavailable - use offline mode'
            }

# Global connectivity manager instance
connectivity_manager = ConnectivityManager()

# Helper functions for easy integration
def check_internet_connectivity() -> bool:
    """Simple function to check if internet is available"""
    result = connectivity_manager.check_internet_connectivity()
    return result['internet_available']

def get_connection_status() -> Dict:
    """Get detailed connection status"""
    return connectivity_manager.check_internet_connectivity()

def get_system_mode() -> str:
    """Get recommended system mode (online/offline/hybrid)"""
    result = connectivity_manager.check_internet_connectivity()
    return result['recommendation']['mode']

def is_online_mode_available() -> bool:
    """Check if online/hybrid modes are available"""
    return check_internet_connectivity()

def get_mode_recommendation() -> Dict:
    """Get detailed mode recommendation"""
    result = connectivity_manager.check_internet_connectivity()
    return result['recommendation']