# MongoDB Schema Documentation
## Truck Utilization Calculator Database

### Database Information
- **Database Name**: `truck_calculator`
- **MongoDB Atlas Cluster**: `cluster0.r6r1vth.mongodb.net`
- **Connection String**: `mongodb+srv://admin:admin123@cluster0.r6r1vth.mongodb.net/`

---

## Collections Schema

### 1. `calculations` Collection
Stores all truck utilization calculations performed by users.

**Document Structure:**
```json
{
  "_id": ObjectId,
  "destination": "string",           // Destination city/location
  "truck_type": "string",           // Selected truck type (Small/Medium/Large)
  "truck_spec": {                   // Truck specifications used
    "volume": "number",             // Volume capacity in m³
    "weight": "number"              // Weight capacity in kg
  },
  "skus": [                         // Array of SKU items
    {
      "name": "string",             // SKU name
      "quantity": "number",         // Quantity of boxes
      "volume_per_box": "number",   // Volume per box in m³
      "weight_per_box": "number",   // Weight per box in kg
      "total_volume": "number",     // Calculated total volume
      "total_weight": "number"      // Calculated total weight
    }
  ],
  "results": {                      // Calculation results
    "total_volume": "number",       // Total volume of all SKUs
    "total_weight": "number",       // Total weight of all SKUs
    "trucks_needed": "number",      // Number of trucks required
    "trucks_needed_volume": "number", // Trucks needed based on volume
    "trucks_needed_weight": "number", // Trucks needed based on weight
    "utilization_percentage": "number", // Overall utilization %
    "limiting_factor": "string",    // 'volume' or 'weight'
    "volume_utilization": "number", // Volume utilization %
    "weight_utilization": "number"  // Weight utilization %
  },
  "timestamp": "datetime"           // When calculation was performed
}
```

**Indexes:**
- `timestamp: -1` (descending, for recent calculations)
- `destination: 1` (ascending, for filtering by destination)
- `truck_type: 1` (ascending, for filtering by truck type)

---

### 2. `sku_templates` Collection
Stores reusable SKU configurations for quick loading.

**Document Structure:**
```json
{
  "_id": ObjectId,
  "template_name": "string",        // Unique template name
  "skus": [                         // Array of SKU configurations
    {
      "name": "string",             // SKU name
      "quantity": "number",         // Default quantity
      "volume_per_box": "number",   // Volume per box in m³
      "weight_per_box": "number"    // Weight per box in kg
    }
  ],
  "created_at": "datetime",         // Template creation date
  "updated_at": "datetime"          // Last modification date
}
```

**Indexes:**
- `template_name: 1` (unique, for template lookup)
- `updated_at: -1` (descending, for recent templates)

---

### 3. `truck_configurations` Collection
Stores custom truck type configurations.

**Document Structure:**
```json
{
  "_id": ObjectId,
  "config_name": "string",          // Configuration name
  "truck_types": {                  // Truck type definitions
    "Small": {
      "volume": "number",           // Volume capacity in m³
      "weight": "number"            // Weight capacity in kg
    },
    "Medium": {
      "volume": "number",
      "weight": "number"
    },
    "Large": {
      "volume": "number",
      "weight": "number"
    }
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Indexes:**
- `config_name: 1` (unique, for configuration lookup)

---

### 4. `analytics_summary` Collection
Reserved for future aggregated analytics data.

**Purpose:**
- Store pre-computed analytics for performance
- Historical trend data
- Usage statistics

---

## Sample Data Examples

### Sample Calculation Document:
```json
{
  "destination": "New York",
  "truck_type": "Medium",
  "truck_spec": {
    "volume": 40,
    "weight": 7000
  },
  "skus": [
    {
      "name": "Electronics Box A",
      "quantity": 50,
      "volume_per_box": 0.08,
      "weight_per_box": 2.5,
      "total_volume": 4.0,
      "total_weight": 125.0
    }
  ],
  "results": {
    "total_volume": 4.0,
    "total_weight": 125.0,
    "trucks_needed": 1,
    "utilization_percentage": 10.0,
    "limiting_factor": "volume"
  },
  "timestamp": "2025-05-26T15:30:00Z"
}
```

### Sample SKU Template:
```json
{
  "template_name": "Electronics Standard",
  "skus": [
    {
      "name": "Laptop",
      "quantity": 10,
      "volume_per_box": 0.08,
      "weight_per_box": 3.0
    },
    {
      "name": "Monitor",
      "quantity": 15,
      "volume_per_box": 0.12,
      "weight_per_box": 5.0
    }
  ],
  "created_at": "2025-05-26T15:30:00Z",
  "updated_at": "2025-05-26T15:30:00Z"
}
```

---

## Database Operations

### Common Queries

1. **Get recent calculations:**
```javascript
db.calculations.find().sort({timestamp: -1}).limit(10)
```

2. **Find calculations by destination:**
```javascript
db.calculations.find({destination: "New York"})
```

3. **Get average utilization:**
```javascript
db.calculations.aggregate([
  {$group: {
    _id: null,
    avgUtilization: {$avg: "$results.utilization_percentage"}
  }}
])
```

4. **Load SKU template:**
```javascript
db.sku_templates.findOne({template_name: "Electronics Standard"})
```

### Performance Considerations

- Indexes are created automatically on first connection
- Collections are created as needed
- Consider archiving old calculations periodically
- Monitor document size for large SKU arrays

---

## Security & Access

- **Current Setup**: Basic authentication with admin user
- **Recommended**: Create application-specific user with limited permissions
- **Network**: IP whitelist configured for security
- **SSL**: Enforced through MongoDB Atlas

---

## Backup & Recovery

- MongoDB Atlas provides automatic backups
- Use export functionality in the app for additional backups
- JSON export includes all collections for full data portability

---

## Future Enhancements

1. **Additional Collections:**
   - `users` - User management
   - `audit_logs` - Activity tracking
   - `settings` - Application configuration

2. **Advanced Analytics:**
   - Time-series data for trends
   - Geographical analysis
   - Cost optimization tracking

3. **Performance Optimization:**
   - Compound indexes for complex queries
   - Data archiving strategy
   - Aggregation pipeline optimization