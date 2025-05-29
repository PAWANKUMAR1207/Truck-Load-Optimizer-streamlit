import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from utils.calculations import TruckCalculator
from utils.visualizations import create_utilization_chart, create_sku_breakdown_chart
from utils.optimization import OptimizationEngine
from utils.database import MongoDBManager

# Page configuration
st.set_page_config(
    page_title="Truck Utilization Calculator",
    page_icon="🚛",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'calculation_history' not in st.session_state:
        st.session_state.calculation_history = []
    if 'sku_counter' not in st.session_state:
        st.session_state.sku_counter = 1
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = MongoDBManager()

def add_sku_row():
    """Add a new SKU row"""
    st.session_state.sku_counter += 1

def remove_sku_row():
    """Remove the last SKU row"""
    if st.session_state.sku_counter > 1:
        st.session_state.sku_counter -= 1

def collect_sku_inputs():
    """Collect SKU inputs from the user interface"""
    skus = []
    
    st.subheader("📦 SKU Information")
    
    # Controls for adding/removing SKUs
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("➕ Add SKU", on_click=add_sku_row):
            pass
    with col2:
        if st.button("➖ Remove SKU", on_click=remove_sku_row):
            pass
    
    # SKU input rows
    for i in range(st.session_state.sku_counter):
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                sku_name = st.text_input(
                    f"SKU Name",
                    key=f"sku_name_{i}",
                    placeholder=f"Enter SKU {i+1} name"
                )
            
            with col2:
                quantity = st.number_input(
                    f"Quantity",
                    min_value=0,
                    value=1,
                    key=f"quantity_{i}"
                )
            
            with col3:
                volume_per_box = st.number_input(
                    f"Volume/Box (m³)",
                    min_value=0.0,
                    value=0.1,
                    step=0.01,
                    format="%.3f",
                    key=f"volume_{i}"
                )
            
            with col4:
                weight_per_box = st.number_input(
                    f"Weight/Box (kg)",
                    min_value=0.0,
                    value=10.0,
                    step=0.1,
                    format="%.1f",
                    key=f"weight_{i}"
                )
            
            with col5:
                # Calculate totals for this SKU
                total_volume = quantity * volume_per_box
                total_weight = quantity * weight_per_box
                st.metric("Total Vol.", f"{total_volume:.2f} m³")
                st.metric("Total Weight", f"{total_weight:.1f} kg")
            
            if sku_name and quantity > 0:
                skus.append({
                    'name': sku_name,
                    'quantity': quantity,
                    'volume_per_box': volume_per_box,
                    'weight_per_box': weight_per_box,
                    'total_volume': total_volume,
                    'total_weight': total_weight
                })
    
    return skus

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🚛 Truck Utilization Calculator")
    st.markdown("Optimize your logistics planning with multi-SKU analysis and efficiency recommendations")
    
    # Sidebar for truck configurations and database features
    st.sidebar.header("🚚 Truck Configurations")
    
    # Database features section
    db_manager = st.session_state.db_manager
    if db_manager.connected:
        st.sidebar.success("✅ MongoDB Connected")
        
        # Database management section
        st.sidebar.markdown("---")
        st.sidebar.subheader("🗄️ Database Management")
        
        if st.sidebar.button("📈 View Analytics Dashboard"):
            st.session_state.show_analytics = True
        
        if st.sidebar.button("⚙️ View Database Info"):
            st.session_state.show_db_info = True
        
        # Sample data option
        if st.sidebar.button("🎯 Add Sample Data"):
            if db_manager.create_sample_data():
                st.sidebar.success("✅ Sample data added!")
    else:
        st.sidebar.info("📝 Local Storage Mode")
    
    # Predefined truck types with their specifications
    truck_types = {
        "Small": {"volume": 20, "weight": 3000},
        "Medium": {"volume": 40, "weight": 7000},
        "Large": {"volume": 80, "weight": 15000}
    }
    
    # Allow user to modify truck specifications
    st.sidebar.subheader("Truck Specifications")
    for truck_type in truck_types:
        st.sidebar.markdown(f"**{truck_type} Truck:**")
        truck_types[truck_type]["volume"] = st.sidebar.number_input(
            f"{truck_type} - Volume Capacity (m³)",
            min_value=1.0,
            value=float(truck_types[truck_type]["volume"]),
            step=1.0,
            key=f"{truck_type}_volume"
        )
        truck_types[truck_type]["weight"] = st.sidebar.number_input(
            f"{truck_type} - Weight Capacity (kg)",
            min_value=100.0,
            value=float(truck_types[truck_type]["weight"]),
            step=100.0,
            key=f"{truck_type}_weight"
        )
        st.sidebar.markdown("---")
    
    # Main input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Destination input
        destination = st.text_input(
            "🎯 Destination",
            placeholder="Enter destination name"
        )
        
        # Truck type selection
        selected_truck_type = st.selectbox(
            "🚛 Select Truck Type",
            options=list(truck_types.keys()),
            help="Choose the truck type for this shipment"
        )
        
        # SKU Templates section
        st.markdown("---")
        db_manager = st.session_state.db_manager
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Current SKUs as Template"):
                show_save_template_dialog()
        
        with col2:
            if st.button("📋 Load SKU Template"):
                show_load_template_dialog()
        
        # Collect SKU inputs
        skus = collect_sku_inputs()
    
    with col2:
        # Display selected truck specifications
        if selected_truck_type:
            st.subheader("Selected Truck Specs")
            truck_spec = truck_types[selected_truck_type]
            st.metric("Volume Capacity", f"{truck_spec['volume']} m³")
            st.metric("Weight Capacity", f"{truck_spec['weight']} kg")
    
    # Calculate button and results
    if st.button("🔍 Calculate Truck Requirements", type="primary"):
        if not skus:
            st.error("⚠️ Please add at least one SKU with valid information")
            return
        
        if not destination:
            st.error("⚠️ Please enter a destination")
            return
        
        # Perform calculations
        calculator = TruckCalculator(truck_types[selected_truck_type])
        results = calculator.calculate_requirements(skus)
        
        # Store in history (both local and database)
        calculation_data = {
            'destination': destination,
            'truck_type': selected_truck_type,
            'truck_spec': truck_types[selected_truck_type],
            'skus': skus.copy(),
            'results': results,
            'timestamp': pd.Timestamp.now()
        }
        st.session_state.calculation_history.append(calculation_data)
        
        # Save to MongoDB if connected
        db_manager = st.session_state.db_manager
        if db_manager.connected:
            db_manager.save_calculation(calculation_data)
        
        # Display results
        display_results(results, skus, destination, selected_truck_type, truck_types[selected_truck_type])
    
    # Show analytics or database info if requested
    if st.session_state.get('show_analytics', False):
        show_analytics_dashboard(db_manager)
        if st.button("❌ Close Analytics"):
            st.session_state.show_analytics = False
            st.rerun()
    
    if st.session_state.get('show_db_info', False):
        show_database_info(db_manager)
        if st.button("❌ Close Database Info"):
            st.session_state.show_db_info = False
            st.rerun()

def display_results(results, skus, destination, truck_type, truck_spec):
    """Display calculation results"""
    st.markdown("---")
    st.header("📊 Calculation Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Volume", f"{results['total_volume']:.2f} m³")
    
    with col2:
        st.metric("Total Weight", f"{results['total_weight']:.1f} kg")
    
    with col3:
        trucks_needed = results['trucks_needed']
        st.metric("Trucks Required", trucks_needed)
    
    with col4:
        utilization = results['utilization_percentage']
        color = "normal" if utilization >= 70 else "inverse"
        st.metric("Utilization", f"{utilization:.1f}%", delta_color=color)
    
    # Detailed breakdown
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # SKU breakdown table
        st.subheader("📦 SKU Breakdown")
        df_skus = pd.DataFrame(skus)
        if not df_skus.empty:
            df_skus = df_skus[['name', 'quantity', 'total_volume', 'total_weight']]
            df_skus.columns = ['SKU Name', 'Quantity', 'Volume (m³)', 'Weight (kg)']
            st.dataframe(df_skus, use_container_width=True)
    
    with col2:
        # Capacity analysis
        st.subheader("🚛 Capacity Analysis")
        
        # Volume analysis
        volume_utilization = (results['total_volume'] / (truck_spec['volume'] * trucks_needed)) * 100
        st.write(f"**Volume Utilization:** {volume_utilization:.1f}%")
        st.progress(min(volume_utilization / 100, 1.0))
        
        # Weight analysis
        weight_utilization = (results['total_weight'] / (truck_spec['weight'] * trucks_needed)) * 100
        st.write(f"**Weight Utilization:** {weight_utilization:.1f}%")
        st.progress(min(weight_utilization / 100, 1.0))
        
        # Limiting factor
        if results['limiting_factor'] == 'volume':
            st.info("📏 **Limiting Factor:** Volume")
        else:
            st.info("⚖️ **Limiting Factor:** Weight")
    
    # Utilization warnings and recommendations
    if utilization < 70:
        st.warning(f"⚠️ **Low Utilization Warning**")
        st.write("Your truck utilization is below 70%. Consider the following recommendations:")
        
        # Generate optimization suggestions
        optimizer = OptimizationEngine(truck_spec)
        suggestions = optimizer.generate_suggestions(results, skus)
        
        for suggestion in suggestions:
            st.write(f"• {suggestion}")
    else:
        st.success("✅ **Good Utilization** - Your truck usage is efficient!")
    
    # Visualizations
    st.subheader("📈 Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Utilization chart
        fig_utilization = create_utilization_chart(results, truck_spec, trucks_needed)
        st.plotly_chart(fig_utilization, use_container_width=True)
    
    with col2:
        # SKU breakdown chart
        fig_breakdown = create_sku_breakdown_chart(skus)
        st.plotly_chart(fig_breakdown, use_container_width=True)

def show_analytics_dashboard(db_manager):
    """Display analytics dashboard with database insights"""
    st.markdown("---")
    st.header("📊 Analytics Dashboard")
    
    analytics_data = db_manager.get_analytics_data()
    
    if analytics_data.get('total_calculations', 0) == 0:
        st.info("📈 No calculation data available yet. Run some calculations to see analytics!")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Calculations", analytics_data.get('total_calculations', 0))
    
    with col2:
        avg_util = analytics_data.get('avg_utilization', 0)
        st.metric("Average Utilization", f"{avg_util:.1f}%")
    
    with col3:
        avg_trucks = analytics_data.get('avg_trucks_needed', 0)
        st.metric("Avg Trucks Needed", f"{avg_trucks:.1f}")
    
    with col4:
        total_volume = analytics_data.get('total_volume_shipped', 0)
        st.metric("Total Volume Shipped", f"{total_volume:.1f} m³")
    
    # Recent calculations from database
    st.subheader("📋 Recent Database History")
    db_history = db_manager.get_calculation_history(limit=20)
    
    if db_history:
        for calc in db_history:
            with st.expander(f"{calc['destination']} - {calc['truck_type']} ({calc['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**SKUs:** {len(calc['skus'])}")
                    st.write(f"**Trucks:** {calc['results']['trucks_needed']}")
                with col2:
                    st.write(f"**Utilization:** {calc['results']['utilization_percentage']:.1f}%")
                    st.write(f"**Volume:** {calc['results']['total_volume']:.2f} m³")

def show_save_template_dialog():
    """Show dialog to save current SKUs as template"""
    if st.session_state.sku_counter == 0:
        st.warning("⚠️ No SKUs to save as template")
        return
    
    db_manager = st.session_state.db_manager
    if not db_manager.connected:
        st.warning("⚠️ Database not connected. Cannot save templates.")
        return
    
    # Get current SKUs
    skus = []
    for i in range(st.session_state.sku_counter):
        sku_name = st.session_state.get(f"sku_name_{i}", "")
        if sku_name:
            skus.append({
                'name': sku_name,
                'quantity': st.session_state.get(f"quantity_{i}", 1),
                'volume_per_box': st.session_state.get(f"volume_{i}", 0.1),
                'weight_per_box': st.session_state.get(f"weight_{i}", 10.0)
            })
    
    if skus:
        # Show template save form
        with st.form("save_template_form"):
            template_name = st.text_input("Template Name", placeholder="Enter a name for this SKU template")
            submitted = st.form_submit_button("💾 Save Template")
            
            if submitted and template_name:
                success = db_manager.save_sku_template(template_name, skus)
                if success:
                    st.success(f"✅ Template '{template_name}' saved successfully!")
                else:
                    st.error("❌ Failed to save template")

def show_load_template_dialog():
    """Show dialog to load SKU template"""
    db_manager = st.session_state.db_manager
    if not db_manager.connected:
        st.warning("⚠️ Database not connected. Cannot load templates.")
        return
    
    templates = db_manager.get_sku_templates()
    
    if not templates:
        st.info("📝 No saved templates found.")
        return
    
    template_names = [t['template_name'] for t in templates]
    
    with st.form("load_template_form"):
        selected_template = st.selectbox("Select Template", template_names)
        load_button = st.form_submit_button("📋 Load Template")
        
        if load_button and selected_template:
            # Find the selected template
            template_data = next((t for t in templates if t['template_name'] == selected_template), None)
            
            if template_data:
                # Load SKUs into session state
                skus = template_data['skus']
                st.session_state.sku_counter = len(skus)
                
                for i, sku in enumerate(skus):
                    st.session_state[f"sku_name_{i}"] = sku['name']
                    st.session_state[f"quantity_{i}"] = sku['quantity']
                    st.session_state[f"volume_{i}"] = sku['volume_per_box']
                    st.session_state[f"weight_{i}"] = sku['weight_per_box']
                
                st.success(f"✅ Template '{selected_template}' loaded successfully!")
                st.rerun()

def show_database_info(db_manager):
    """Display database schema and connection information"""
    st.markdown("---")
    st.header("🗄️ Database Information")
    
    schema_info = db_manager.get_database_schema_info()
    
    if not schema_info:
        st.error("Unable to retrieve database information")
        return
    
    st.subheader(f"📊 Database: {schema_info.get('database_name', 'Unknown')}")
    st.metric("Total Documents", schema_info.get('total_documents', 0))
    
    # Collections information
    st.subheader("📚 Collections")
    
    for collection_name, info in schema_info.get('collections', {}).items():
        with st.expander(f"Collection: {collection_name}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Documents", info.get('document_count', 0))
            
            with col2:
                indexes = info.get('indexes', [])
                st.write(f"**Indexes:** {len(indexes)}")
                for idx in indexes:
                    if 'name' in idx:
                        st.write(f"• {idx['name']}")
    
    # Export data option
    st.subheader("💾 Data Export")
    if st.button("📥 Export All Data to JSON"):
        export_data = db_manager.export_data_to_json()
        if export_data:
            st.download_button(
                label="⬇️ Download JSON Export",
                data=str(export_data),
                file_name=f"truck_calculator_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# Calculation history sidebar
def show_calculation_history():
    """Display calculation history in sidebar"""
    db_manager = st.session_state.db_manager
    
    # Show database history if connected
    if db_manager.connected:
        st.sidebar.header("🗄️ Database History")
        db_history = db_manager.get_calculation_history(limit=5)
        
        if db_history:
            for calc in db_history:
                with st.sidebar.expander(f"{calc['destination']} - {calc['truck_type']}"):
                    st.write(f"**Time:** {calc['timestamp'].strftime('%H:%M:%S')}")
                    st.write(f"**SKUs:** {len(calc['skus'])}")
                    st.write(f"**Trucks:** {calc['results']['trucks_needed']}")
                    st.write(f"**Utilization:** {calc['results']['utilization_percentage']:.1f}%")
            
            if st.sidebar.button("🗑️ Clear Database History"):
                if db_manager.clear_calculation_history():
                    st.sidebar.success("✅ Database history cleared!")
                    st.rerun()
        else:
            st.sidebar.info("No database history yet")
    
    # Show local session history
    if st.session_state.calculation_history:
        st.sidebar.header("📋 Session History")
        
        for i, calc in enumerate(reversed(st.session_state.calculation_history[-3:])):  # Show last 3
            with st.sidebar.expander(f"{calc['destination']} - {calc['truck_type']}"):
                st.write(f"**Time:** {calc['timestamp'].strftime('%H:%M:%S')}")
                st.write(f"**SKUs:** {len(calc['skus'])}")
                st.write(f"**Trucks:** {calc['results']['trucks_needed']}")
                st.write(f"**Utilization:** {calc['results']['utilization_percentage']:.1f}%")
        
        if st.sidebar.button("🗑️ Clear Session History"):
            st.session_state.calculation_history = []
            st.rerun()

if __name__ == "__main__":
    main()
    show_calculation_history()
