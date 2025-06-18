# MaLDReTH Infrastructure Interactions Collection

A Flask web application for collecting and managing potential infrastructure interactions for the MaLDReTH 2 Working Group meeting.

## 🚀 Quick Start

### Heroku Deployment (Free)

```bash
# Clone repository
git clone https://github.com/adammoore/maldreth-infrastructure-interactions.git
cd maldreth-infrastructure-interactions

# Deploy to Heroku
heroku login
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
git push heroku main
heroku open
```

### Local Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py init-db
python app.py
```

## 📊 Features

- Web interface for data collection
- CSV export functionality
- Google Sheets integration
- RESTful API
- Responsive design
- Free Heroku deployment

## 🔧 Setup Instructions

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed setup instructions.

## 📋 Google Integration

See [GOOGLE_FORM_SETUP.md](GOOGLE_FORM_SETUP.md) for Google Sheets and Forms setup.

## 🛠 Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test locally
5. Submit pull request

## 📄 License

Apache 2.0 License - see LICENSE file for details.

## 🎯 MaLDReTH Working Group

This tool supports the MaLDReTH 2 Working Group meeting for collecting infrastructure interaction data.

- **Working Group**: [RDA MaLDReTH](https://www.rd-alliance.org/groups/rda-ofr-mapping-landscape-digital-research-tools-wg/)
- **Repository**: https://github.com/adammoore/maldreth-infrastructure-interactions
