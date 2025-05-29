import math
from typing import List, Dict, Any

class TruckCalculator:
    """Handles all truck utilization calculations"""
    
    def __init__(self, truck_spec: Dict[str, float]):
        """
        Initialize calculator with truck specifications
        
        Args:
            truck_spec: Dictionary containing 'volume' and 'weight' capacity
        """
        self.truck_volume_capacity = truck_spec['volume']
        self.truck_weight_capacity = truck_spec['weight']
    
    def calculate_requirements(self, skus: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate truck requirements for given SKUs
        
        Args:
            skus: List of SKU dictionaries with volume and weight info
            
        Returns:
            Dictionary containing calculation results
        """
        if not skus:
            return {
                'total_volume': 0,
                'total_weight': 0,
                'trucks_needed': 0,
                'utilization_percentage': 0,
                'limiting_factor': None
            }
        
        # Calculate totals
        total_volume = sum(sku['total_volume'] for sku in skus)
        total_weight = sum(sku['total_weight'] for sku in skus)
        
        # Calculate trucks needed based on each constraint
        trucks_needed_volume = math.ceil(total_volume / self.truck_volume_capacity) if total_volume > 0 else 0
        trucks_needed_weight = math.ceil(total_weight / self.truck_weight_capacity) if total_weight > 0 else 0
        
        # The actual trucks needed is the maximum of both constraints
        trucks_needed = max(trucks_needed_volume, trucks_needed_weight)
        
        # Determine limiting factor
        limiting_factor = 'volume' if trucks_needed_volume >= trucks_needed_weight else 'weight'
        
        # Calculate utilization percentage
        if trucks_needed > 0:
            if limiting_factor == 'volume':
                utilization_percentage = (total_volume / (self.truck_volume_capacity * trucks_needed)) * 100
            else:
                utilization_percentage = (total_weight / (self.truck_weight_capacity * trucks_needed)) * 100
        else:
            utilization_percentage = 0
        
        return {
            'total_volume': total_volume,
            'total_weight': total_weight,
            'trucks_needed': trucks_needed,
            'trucks_needed_volume': trucks_needed_volume,
            'trucks_needed_weight': trucks_needed_weight,
            'utilization_percentage': utilization_percentage,
            'limiting_factor': limiting_factor,
            'volume_utilization': (total_volume / (self.truck_volume_capacity * trucks_needed)) * 100 if trucks_needed > 0 else 0,
            'weight_utilization': (total_weight / (self.truck_weight_capacity * trucks_needed)) * 100 if trucks_needed > 0 else 0
        }
    
    def calculate_spare_capacity(self, results: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate spare capacity in the allocated trucks
        
        Args:
            results: Results from calculate_requirements
            
        Returns:
            Dictionary with spare volume and weight capacity
        """
        trucks_needed = results['trucks_needed']
        total_volume = results['total_volume']
        total_weight = results['total_weight']
        
        total_volume_capacity = self.truck_volume_capacity * trucks_needed
        total_weight_capacity = self.truck_weight_capacity * trucks_needed
        
        spare_volume = total_volume_capacity - total_volume
        spare_weight = total_weight_capacity - total_weight
        
        return {
            'spare_volume': spare_volume,
            'spare_weight': spare_weight,
            'spare_volume_percentage': (spare_volume / total_volume_capacity) * 100 if total_volume_capacity > 0 else 0,
            'spare_weight_percentage': (spare_weight / total_weight_capacity) * 100 if total_weight_capacity > 0 else 0
        }
    
    def optimize_truck_type(self, skus: List[Dict[str, Any]], truck_types: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Find the most efficient truck type for given SKUs
        
        Args:
            skus: List of SKU dictionaries
            truck_types: Dictionary of truck types with their specifications
            
        Returns:
            Dictionary with optimization results for each truck type
        """
        optimization_results = {}
        
        for truck_name, truck_spec in truck_types.items():
            calculator = TruckCalculator(truck_spec)
            results = calculator.calculate_requirements(skus)
            
            optimization_results[truck_name] = {
                'trucks_needed': results['trucks_needed'],
                'utilization': results['utilization_percentage'],
                'total_capacity_volume': truck_spec['volume'] * results['trucks_needed'],
                'total_capacity_weight': truck_spec['weight'] * results['trucks_needed']
            }
        
        return optimization_results
