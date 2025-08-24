# PRISM API Documentation

## Overview
PRISM provides comprehensive RESTful API endpoints for accessing tool and interaction data programmatically.

## Base URL
- **Production**: `https://mal2-data-survey-cb27f6674f20.herokuapp.com/`
- **Local Development**: `http://localhost:5001/`

## Authentication
Most endpoints are currently public. Authentication may be required for write operations in future versions.

## Endpoints

### Tools API

#### Get All Tools
```bash
GET /api/v1/tools
```
Returns complete catalog of research tools with metadata.

**Response Format**:
```json
{
  "tools": [
    {
      "id": 1,
      "name": "Tool Name",
      "description": "Tool description",
      "provider": "Provider Name",
      "url": "https://tool-url.com",
      "is_open_source": true,
      "category": "Tool Category",
      "lifecycle_stages": ["PLAN", "COLLECT"]
    }
  ],
  "count": 338
}
```

#### Get Specific Tool
```bash
GET /api/v1/tools/{id}
```

### Interactions API

#### Get All Interactions
```bash
GET /api/v1/interactions
```
Returns complete interaction database with relationships.

**Response Format**:
```json
{
  "interactions": [
    {
      "id": 1,
      "source_tool": "Source Tool Name",
      "target_tool": "Target Tool Name", 
      "interaction_type": "API Integration",
      "lifecycle_stage": "ANALYSE",
      "description": "Integration description",
      "technical_details": "Implementation details",
      "benefits": "Integration benefits",
      "challenges": "Known challenges"
    }
  ],
  "count": 150
}
```

#### Submit New Interaction
```bash
POST /api/interactions
Content-Type: application/json

{
  "source_tool_id": 1,
  "target_tool_id": 2,
  "interaction_type": "API Integration",
  "lifecycle_stage": "ANALYSE",
  "description": "Integration description",
  "technical_details": "Implementation details"
}
```

### Lifecycle API

#### Get All Stages
```bash
GET /api/v1/stages
```
Returns MaLDReTH lifecycle stages with tool counts.

### Export/Import

#### Export CSV Data
```bash
GET /export/interactions/csv
```
Downloads complete interaction data as CSV file.

#### Import CSV Data
```bash
POST /upload/interactions/csv
Content-Type: multipart/form-data

Form field: csv_file
```

## Rate Limits
- Currently no rate limits applied
- Fair use policy in effect
- Contact for high-volume API usage

## Error Handling

### Error Response Format
```json
{
  "error": "Error description",
  "code": 400,
  "details": "Additional error details"
}
```

### Common Status Codes
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Usage Examples

### Python
```python
import requests

# Get all tools
response = requests.get('https://mal2-data-survey-cb27f6674f20.herokuapp.com/api/v1/tools')
tools = response.json()

# Get interactions
response = requests.get('https://mal2-data-survey-cb27f6674f20.herokuapp.com/api/v1/interactions')
interactions = response.json()
```

### cURL
```bash
# Get tools
curl -H "Accept: application/json" \
  https://mal2-data-survey-cb27f6674f20.herokuapp.com/api/v1/tools

# Export CSV
curl -O https://mal2-data-survey-cb27f6674f20.herokuapp.com/export/interactions/csv
```

### JavaScript
```javascript
// Fetch tools
fetch('https://mal2-data-survey-cb27f6674f20.herokuapp.com/api/v1/tools')
  .then(response => response.json())
  .then(data => console.log(data));

// Submit interaction
fetch('https://mal2-data-survey-cb27f6674f20.herokuapp.com/api/interactions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    source_tool_id: 1,
    target_tool_id: 2,
    interaction_type: 'API Integration',
    lifecycle_stage: 'ANALYSE'
  })
});
```

## Data Formats

### CSV Format
For CSV import/export, use the following columns:
- Source Tool (required)
- Target Tool (required) 
- Interaction Type (required)
- Lifecycle Stage (required)
- Description (optional)
- Technical Details (optional)
- Benefits (optional)
- Challenges (optional)

### Interaction Types
- API Integration
- Data Exchange
- Metadata Exchange  
- File Format Conversion
- Workflow Integration
- Plugin/Extension
- Direct Database Connection
- Web Service
- Command Line Interface
- Import/Export
- Other

### Lifecycle Stages
- CONCEPTUALISE
- PLAN
- COLLECT
- PROCESS
- ANALYSE
- STORE
- PUBLISH
- PRESERVE
- SHARE
- ACCESS
- TRANSFORM
- FUND

## Integration Examples

### Tool Discovery Integration
```python
def get_tools_by_stage(stage):
    response = requests.get(f'/api/v1/tools?stage={stage}')
    return response.json()['tools']

# Get analysis tools
analysis_tools = get_tools_by_stage('ANALYSE')
```

### Interaction Mapping
```python
def get_tool_interactions(tool_id):
    response = requests.get(f'/api/v1/interactions?tool_id={tool_id}')
    return response.json()['interactions']

# Find all interactions for a specific tool
interactions = get_tool_interactions(42)
```

## Support

For API support and integration questions:
- GitHub Issues: https://github.com/adammoore/maldreth-infrastructure-interactions/issues
- Documentation: https://mal2-data-survey-cb27f6674f20.herokuapp.com/information-structures
- Community: MaLDReTH II RDA Working Group