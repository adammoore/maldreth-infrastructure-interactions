# MaLDReTH Tool Interactions Integration Guide

## Integration Summary

This guide explains how the MaLDReTH tool interactions functionality has been integrated with your existing project.

## Project Analysis

**Existing Structure:**
- Flask App: ✅ Found
- Database: ❌ Not found
- Templates: ✅ Found
- Requirements: ✅ Found

**Files Added:**
- `database_init.py` - Enhanced database initialization
- `interactions_blueprint.py` - Flask blueprint for interactions
- `templates/interactions/` - HTML templates
- `integration_guide.md` - This guide

## Integration Steps

### 1. Database Setup

Initialize the enhanced database:
```bash
python database_init.py
```

### 2. Flask Integration

If you have an existing Flask app, integrate the blueprint:

```python
from flask import Flask
from interactions_blueprint import register_interactions_blueprint

app = Flask(__name__)

# Register the interactions blueprint
register_interactions_blueprint(app)

if __name__ == '__main__':
    app.run(debug=True)
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Access the Functionality

- Web Interface: `http://localhost:5000/interactions/`
- API Endpoints: 
  - `http://localhost:5000/interactions/api/interactions`
  - `http://localhost:5000/interactions/api/stats`

## API Usage Examples

### Get All Interactions
```python
import requests

response = requests.get('http://localhost:5000/interactions/api/interactions')
interactions = response.json()
```

### Filter Interactions
```python
# Filter by stage
response = requests.get('http://localhost:5000/interactions/api/interactions?stage=Analyse')

# Filter by type and complexity
response = requests.get('http://localhost:5000/interactions/api/interactions?type=data_flow&complexity=medium')
```

### Get Statistics
```python
response = requests.get('http://localhost:5000/interactions/api/stats')
stats = response.json()
print(f"Total interactions: {stats['total_interactions']}")
```

## Customization

### Adding Custom Interactions

```python
from interactions_blueprint import interactions_service

# Add your custom interaction data
interaction_data = {
    'source_tool_id': 1,
    'target_tool_id': 2,
    'interaction_type': 'data_flow',
    'description': 'Your custom interaction description',
    # ... other fields
}

# Use the service to add to database
```

### Extending the Blueprint

You can extend the blueprint by adding new routes:

```python
from interactions_blueprint import interactions_bp

@interactions_bp.route('/custom-endpoint')
def custom_endpoint():
    # Your custom functionality
    return jsonify({'message': 'Custom endpoint'})
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Errors**: Run `database_init.py` to initialize the database
3. **Template Not Found**: Check that templates are in the correct directory

### Support

For technical issues, refer to the main project documentation or create an issue on the GitHub repository.

## Next Steps

1. Customize the templates to match your existing design
2. Add authentication if required
3. Extend the database schema for your specific needs
4. Add more interaction examples relevant to your research domain

