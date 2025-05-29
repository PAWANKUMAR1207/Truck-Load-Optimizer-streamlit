import random
from typing import List, Dict, Any

class OptimizationEngine:
    """Provides optimization suggestions for truck utilization"""
    
    def __init__(self, truck_spec: Dict[str, float]):
        """
        Initialize optimization engine
        
        Args:
            truck_spec: Dictionary containing truck specifications
        """
        self.truck_volume_capacity = truck_spec['volume']
        self.truck_weight_capacity = truck_spec['weight']
    
    def generate_suggestions(self, results: Dict[str, Any], skus: List[Dict[str, Any]]) -> List[str]:
        """
        Generate optimization suggestions based on current utilization
        
        Args:
            results: Calculation results
            skus: List of current SKUs
            
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        utilization = results['utilization_percentage']
        limiting_factor = results['limiting_factor']
        trucks_needed = results['trucks_needed']
        
        # Calculate spare capacity
        if limiting_factor == 'volume':
            spare_capacity = (self.truck_volume_capacity * trucks_needed) - results['total_volume']
            capacity_unit = 'm³'
        else:
            spare_capacity = (self.truck_weight_capacity * trucks_needed) - results['total_weight']
            capacity_unit = 'kg'
        
        # Basic utilization improvement suggestions
        if utilization < 50:
            suggestions.append(f"Consider consolidating shipments - you have {spare_capacity:.2f} {capacity_unit} of unused capacity")
            suggestions.append("Look for additional SKUs going to the same destination or nearby locations")
        elif utilization < 70:
            suggestions.append(f"You can add {spare_capacity:.2f} {capacity_unit} more cargo to improve efficiency")
            suggestions.append("Consider adding fast-moving items to fill the remaining space")
        
        # SKU-specific suggestions
        if skus:
            suggestions.extend(self._generate_sku_specific_suggestions(skus, spare_capacity, limiting_factor))
        
        # Alternative truck type suggestions
        suggestions.extend(self._generate_truck_type_suggestions(results, skus))
        
        # Route optimization suggestions
        suggestions.extend(self._generate_route_suggestions())
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _generate_sku_specific_suggestions(self, skus: List[Dict[str, Any]], spare_capacity: float, limiting_factor: str) -> List[str]:
        """Generate suggestions specific to current SKUs"""
        suggestions = []
        
        # Find SKUs with potential for quantity increases
        for sku in skus:
            if limiting_factor == 'volume':
                additional_units = int(spare_capacity / sku['volume_per_box'])
            else:
                additional_units = int(spare_capacity / sku['weight_per_box'])
            
            if additional_units > 0:
                suggestions.append(f"Add {additional_units} more units of '{sku['name']}' to improve utilization")
                break  # Only suggest for one SKU to avoid clutter
        
        # Suggest combining similar SKUs
        if len(skus) > 1:
            suggestions.append("Consider combining similar SKUs into a single shipment")
        
        return suggestions
    
    def _generate_truck_type_suggestions(self, results: Dict[str, Any], skus: List[Dict[str, Any]]) -> List[str]:
        """Generate truck type optimization suggestions"""
        suggestions = []
        
        # This is a simplified suggestion - in practice, you'd calculate for different truck types
        if results['utilization_percentage'] < 60:
            suggestions.append("Consider using a smaller truck type if available for better cost efficiency")
        elif results['utilization_percentage'] > 95:
            suggestions.append("Consider using a larger truck type to accommodate future growth")
        
        return suggestions
    
    def _generate_route_suggestions(self) -> List[str]:
        """Generate route and logistics optimization suggestions"""
        suggestions = [
            "Check for nearby destinations that could be combined in the same route",
            "Consider scheduling flexibility to combine multiple orders",
            "Evaluate if partial shipments could be consolidated with future orders"
        ]
        
        # Return a random selection to provide variety
        return random.sample(suggestions, min(2, len(suggestions)))
    
    def calculate_optimal_quantities(self, skus: List[Dict[str, Any]], target_utilization: float = 85.0) -> Dict[str, Any]:
        """
        Calculate optimal quantities to achieve target utilization
        
        Args:
            skus: List of current SKUs
            target_utilization: Target utilization percentage (default 85%)
            
        Returns:
            Dictionary with optimization recommendations
        """
        if not skus:
            return {}
        
        # Calculate current totals
        current_volume = sum(sku['total_volume'] for sku in skus)
        current_weight = sum(sku['total_weight'] for sku in skus)
        
        # Calculate required trucks for current load
        trucks_needed_volume = max(1, int(current_volume / self.truck_volume_capacity) + 1)
        trucks_needed_weight = max(1, int(current_weight / self.truck_weight_capacity) + 1)
        trucks_needed = max(trucks_needed_volume, trucks_needed_weight)
        
        # Calculate target capacity
        target_volume = (self.truck_volume_capacity * trucks_needed) * (target_utilization / 100)
        target_weight = (self.truck_weight_capacity * trucks_needed) * (target_utilization / 100)
        
        # Calculate additional capacity needed
        additional_volume_needed = max(0, target_volume - current_volume)
        additional_weight_needed = max(0, target_weight - current_weight)
        
        # Generate recommendations for each SKU
        recommendations = {}
        for sku in skus:
            if additional_volume_needed > 0 and sku['volume_per_box'] > 0:
                additional_units_volume = int(additional_volume_needed / sku['volume_per_box'])
            else:
                additional_units_volume = 0
            
            if additional_weight_needed > 0 and sku['weight_per_box'] > 0:
                additional_units_weight = int(additional_weight_needed / sku['weight_per_box'])
            else:
                additional_units_weight = 0
            
            # Take the minimum to ensure we don't exceed either constraint
            additional_units = min(additional_units_volume, additional_units_weight)
            
            if additional_units > 0:
                recommendations[sku['name']] = {
                    'current_quantity': sku['quantity'],
                    'recommended_additional': additional_units,
                    'new_total': sku['quantity'] + additional_units
                }
        
        return {
            'target_utilization': target_utilization,
            'current_utilization': (max(current_volume/self.truck_volume_capacity, current_weight/self.truck_weight_capacity) / trucks_needed) * 100,
            'trucks_needed': trucks_needed,
            'recommendations': recommendations
        }
