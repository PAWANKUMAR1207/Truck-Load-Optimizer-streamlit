import pymongo
from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Any, Optional
import streamlit as st
import os

class MongoDBManager:
    """Handles all MongoDB operations for the truck utilization calculator"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = None
        self.db = None
        self.connected = False
        self.connect()
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            # Get MongoDB connection string from environment or use your cluster
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb+srv://admin:admin123@cluster0.r6r1vth.mongodb.net/')
            
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client['truck_calculator']
            
            # Test the connection
            self.client.admin.command('ping')
            self.connected = True
            
            # Initialize collections and indexes
            self._setup_database()
            
            st.success("✅ Connected to MongoDB Atlas cluster successfully!")
            return True
            
        except Exception as e:
            self.connected = False
            st.info(f"📝 Using local storage - MongoDB connection failed: {str(e)}")
            return False
    
    def _setup_database(self):
        """Initialize database collections and create indexes"""
        if not self.connected or self.client is None:
            return
            
        try:
            # Create collections if they don't exist
            collections = self.db.list_collection_names()
            
            # Setup calculations collection
            if 'calculations' not in collections:
                self.db.create_collection('calculations')
            
            # Create indexes for better performance
            try:
                self.db.calculations.create_index([('timestamp', -1)])
                self.db.calculations.create_index([('destination', 1)])
                self.db.calculations.create_index([('truck_type', 1)])
            except:
                pass  # Indexes might already exist
            
            # Setup SKU templates collection
            if 'sku_templates' not in collections:
                self.db.create_collection('sku_templates')
            
            try:
                self.db.sku_templates.create_index([('template_name', 1)], unique=True)
                self.db.sku_templates.create_index([('updated_at', -1)])
            except:
                pass
            
            # Setup truck configurations collection
            if 'truck_configurations' not in collections:
                self.db.create_collection('truck_configurations')
            
            try:
                self.db.truck_configurations.create_index([('config_name', 1)], unique=True)
            except:
                pass
            
        except Exception as e:
            st.warning(f"Database setup completed with some warnings: {str(e)}")
    
    def save_calculation(self, calculation_data: Dict[str, Any]) -> Optional[str]:
        """Save a calculation to the database"""
        if not self.connected or self.client is None:
            return None
            
        try:
            # Add timestamp if not present
            if 'timestamp' not in calculation_data:
                calculation_data['timestamp'] = datetime.now()
            
            # Insert into calculations collection
            result = self.db.calculations.insert_one(calculation_data)
            return str(result.inserted_id)
            
        except Exception as e:
            st.error(f"Failed to save calculation: {str(e)}")
            return None
    
    def get_calculation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve calculation history from database"""
        if not self.connected or self.client is None:
            return []
            
        try:
            # Get recent calculations sorted by timestamp
            calculations = list(
                self.db.calculations
                .find({}, {'_id': 0})  # Exclude MongoDB _id from results
                .sort('timestamp', -1)
                .limit(limit)
            )
            
            return calculations
            
        except Exception as e:
            st.error(f"Failed to retrieve calculation history: {str(e)}")
            return []
    
    def save_sku_template(self, template_name: str, skus: List[Dict[str, Any]]) -> bool:
        """Save SKU configuration as a reusable template"""
        if not self.connected or self.client is None:
            return False
            
        try:
            template_data = {
                'template_name': template_name,
                'skus': skus,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Use upsert to update existing template or create new one
            self.db.sku_templates.replace_one(
                {'template_name': template_name},
                template_data,
                upsert=True
            )
            
            return True
            
        except Exception as e:
            st.error(f"Failed to save SKU template: {str(e)}")
            return False
    
    def get_sku_templates(self) -> List[Dict[str, Any]]:
        """Retrieve all saved SKU templates"""
        if not self.connected or self.client is None:
            return []
            
        try:
            templates = list(
                self.db.sku_templates
                .find({}, {'_id': 0})
                .sort('updated_at', -1)
            )
            
            return templates
            
        except Exception as e:
            st.error(f"Failed to retrieve SKU templates: {str(e)}")
            return []
    
    def delete_sku_template(self, template_name: str) -> bool:
        """Delete a SKU template"""
        if not self.connected or self.client is None:
            return False
            
        try:
            result = self.db.sku_templates.delete_one({'template_name': template_name})
            return result.deleted_count > 0
            
        except Exception as e:
            st.error(f"Failed to delete SKU template: {str(e)}")
            return False
    
    def get_analytics_data(self) -> Dict[str, Any]:
        """Get analytics data from stored calculations"""
        if not self.connected or self.client is None:
            return {}
            
        try:
            # Get total calculations
            total_calculations = self.db.calculations.count_documents({})
            
            if total_calculations == 0:
                return {
                    'total_calculations': 0,
                    'avg_utilization': 0,
                    'avg_trucks_needed': 0,
                    'total_volume_shipped': 0,
                    'total_weight_shipped': 0
                }
            
            # Get average utilization using aggregation
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'avg_utilization': {'$avg': '$results.utilization_percentage'},
                        'avg_trucks_needed': {'$avg': '$results.trucks_needed'},
                        'total_volume_shipped': {'$sum': '$results.total_volume'},
                        'total_weight_shipped': {'$sum': '$results.total_weight'}
                    }
                }
            ]
            
            result = list(self.db.calculations.aggregate(pipeline))
            
            if result:
                analytics = result[0]
                analytics['total_calculations'] = total_calculations
                analytics.pop('_id', None)  # Remove MongoDB _id
                return analytics
            else:
                return {
                    'total_calculations': total_calculations,
                    'avg_utilization': 0,
                    'avg_trucks_needed': 0,
                    'total_volume_shipped': 0,
                    'total_weight_shipped': 0
                }
                
        except Exception as e:
            st.error(f"Failed to retrieve analytics data: {str(e)}")
            return {}
    
    def clear_calculation_history(self) -> bool:
        """Clear all calculation history"""
        if not self.connected or self.client is None:
            return False
            
        try:
            self.db.calculations.delete_many({})
            return True
            
        except Exception as e:
            st.error(f"Failed to clear calculation history: {str(e)}")
            return False
    
    def get_database_schema_info(self) -> Dict[str, Any]:
        """Get information about the database schema and collections"""
        if not self.connected or self.client is None:
            return {}
            
        try:
            schema_info = {
                'database_name': self.db.name,
                'collections': {},
                'total_documents': 0
            }
            
            collections = self.db.list_collection_names()
            
            for collection_name in collections:
                collection = self.db[collection_name]
                doc_count = collection.count_documents({})
                
                schema_info['collections'][collection_name] = {
                    'document_count': doc_count,
                    'indexes': []  # Simplified for now
                }
                schema_info['total_documents'] += doc_count
            
            return schema_info
            
        except Exception as e:
            st.error(f"Failed to get schema info: {str(e)}")
            return {}
    
    def create_sample_data(self) -> bool:
        """Create sample data for demonstration (only if collections are empty)"""
        if not self.connected or self.client is None:
            return False
            
        try:
            # Only create sample data if collections are empty
            if self.db.calculations.count_documents({}) == 0:
                sample_calculations = [
                    {
                        'destination': 'New York',
                        'truck_type': 'Medium',
                        'truck_spec': {'volume': 40, 'weight': 7000},
                        'skus': [
                            {'name': 'Electronics A', 'quantity': 50, 'volume_per_box': 0.08, 'weight_per_box': 2.5, 'total_volume': 4.0, 'total_weight': 125.0}
                        ],
                        'results': {
                            'total_volume': 4.0,
                            'total_weight': 125.0,
                            'trucks_needed': 1,
                            'utilization_percentage': 10.0,
                            'limiting_factor': 'volume'
                        },
                        'timestamp': datetime.now()
                    }
                ]
                
                self.db.calculations.insert_many(sample_calculations)
            
            # Create sample SKU template if none exist
            if self.db.sku_templates.count_documents({}) == 0:
                sample_template = {
                    'template_name': 'Electronics Standard',
                    'skus': [
                        {'name': 'Laptop', 'quantity': 10, 'volume_per_box': 0.08, 'weight_per_box': 3.0},
                        {'name': 'Monitor', 'quantity': 15, 'volume_per_box': 0.12, 'weight_per_box': 5.0}
                    ],
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                
                self.db.sku_templates.insert_one(sample_template)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to create sample data: {str(e)}")
            return False
    
    def export_data_to_json(self) -> Dict[str, Any]:
        """Export all data to JSON format for backup"""
        if not self.connected or self.client is None:
            return {}
            
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'calculations': list(self.db.calculations.find({}, {'_id': 0})),
                'sku_templates': list(self.db.sku_templates.find({}, {'_id': 0}))
            }
            
            return export_data
            
        except Exception as e:
            st.error(f"Failed to export data: {str(e)}")
            return {}
    
    def close_connection(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()