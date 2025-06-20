# MaLDReTH Infrastructure Interactions Collection

A Flask web application for collecting and managing potential infrastructure interactions for the MaLDReTH 2 Working Group meeting.

## 🚀 Quick Start

### Heroku Deployment (Recommended)

1. **Prerequisites**:
   - Git installed
   - Heroku CLI installed (`brew install heroku/brew/heroku` on macOS)
   - Heroku account (free)

2. **Deploy**:
   ```bash
   git clone https://github.com/adammoore/maldreth-infrastructure-interactions.git
   cd maldreth-infrastructure-interactions
   heroku login
   heroku create your-app-name
   heroku addons:create heroku-postgresql:mini
   git push heroku main
   heroku open
   ```

### Local Development

1. **Setup**:
   ```bash
   git clone https://github.com/adammoore/maldreth-infrastructure-interactions.git
   cd maldreth-infrastructure-interactions
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   python app.py init-db
   python app.py
   ```

2. **Access**: http://localhost:5000

## 📊 Features

- **Web Interface**: Easy-to-use forms for data collection
- **Data Export**: CSV export for analysis and sharing
- **API Access**: RESTful API for programmatic access
- **Responsive Design**: Works on desktop and mobile
- **PostgreSQL**: Production-ready database on Heroku

## 🔧 Data Model

The application collects:
- **Core Information**: Interaction type, source/target infrastructure, lifecycle stage
- **Technical Details**: Implementation specifics, standards, protocols
- **Impact Assessment**: Benefits, challenges, examples
- **Contact Info**: Person, organization, email
- **Classification**: Priority, complexity, status

## 📋 Google Sheets Integration

### Manual Setup

1. **Create Google Sheet**:
   - Import `google_sheets_template.csv` to Google Sheets
   - Share with collaborators
   - Use for data analysis and visualization

2. **Create Google Form**:
   - Follow instructions in `google_form_setup.md`
   - Link responses to your Google Sheet
   - Share form link for data collection

### Automatic Setup (Optional)

If you need automatic Google integration:

1. **Enable Google APIs**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing
   - Enable Google Sheets API and Google Forms API
   - Create credentials (OAuth 2.0)

2. **Configure App**:
   ```bash
   heroku config:set GOOGLE_CLIENT_ID=your-client-id
   heroku config:set GOOGLE_CLIENT_SECRET=your-client-secret
   ```

## 📝 Usage

### Adding Interactions

1. Visit your deployed app
2. Click "Add Interaction"
3. Fill out the form with interaction details
4. Submit to save to database

### Viewing Data

1. Click "View All" to see all interactions
2. Use "Export CSV" to download data
3. Import CSV to Google Sheets for analysis

### API Access

```bash
# Get all interactions
curl https://your-app.herokuapp.com/api/interactions

# Add new interaction (POST JSON)
curl -X POST https://your-app.herokuapp.com/api/interactions \
  -H "Content-Type: application/json" \
  -d '{"interaction_type": "data_flow", ...}'
```

## 🔄 Updating the App

```bash
git pull origin main
git push heroku main
```

## 💰 Costs

- **Heroku Hobby Tier**: Free for 550 hours/month (enough for workshops)
- **PostgreSQL Mini**: Free up to 10,000 rows
- **Google APIs**: Free quota sufficient for most use cases

## 🛠 Troubleshooting

### Common Issues

1. **App won't start**: Check `heroku logs --tail`
2. **Database errors**: Ensure PostgreSQL addon is added
3. **Form errors**: Check field validation in browser console

### Support

- Create issues on GitHub
- Check Heroku documentation
- Contact MaLDReTH working group

## 📊 Example Data Structure

| Field | Example | Required |
|-------|---------|----------|
| Interaction Type | Data Flow | Yes |
| Source Infrastructure | Research Repository | Yes |
| Target Infrastructure | Analysis Platform | Yes |
| Lifecycle Stage | Analyse | Yes |
| Description | Automated data transfer... | Yes |
| Technical Details | REST API, OAuth 2.0 | No |
| Benefits | Seamless integration | No |
| Challenges | Network latency | No |
| Contact Person | Dr. Jane Smith | No |
| Organization | University XYZ | No |
| Priority | High | No |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test locally
5. Submit pull request

## 📄 License

Apache 2.0 License - see LICENSE file for details.

## 🎯 MaLDReTH Working Group

This tool supports the MaLDReTH 2 Working Group meeting for collecting infrastructure interaction data across the research data lifecycle.

- **Working Group**: [RDA MaLDReTH](https://www.rd-alliance.org/groups/rda-ofr-mapping-landscape-digital-research-tools-wg/)
- **Documentation**: See project deliverables for context
- **Support**: Contact working group coordinators
