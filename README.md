# Fashion Recommendation System

A modern, responsive web application for fashion recommendations with sustainability features, built with Flask and Streamlit.

## 🌟 Features

- **Fashion Recommendations**: Upload images to get personalized fashion suggestions
- **Sustainability Scoring**: Check the environmental impact of clothing items
- **Community Voting**: Rate and comment on fashion items
- **Responsive Design**: Works perfectly on all devices (mobile, tablet, desktop)
- **Admin Dashboard**: Manage products, users, and ratings
- **Real-time Interface**: Interactive Streamlit recommendation system

## 🚀 Live Demo

- **Main Application**: [http://fashion.dreamware.lk](http://fashion.dreamware.lk)
- **Recommendation Interface**: [http://fashion.dreamware.lk/recommendations/](http://fashion.dreamware.lk/recommendations/)

## 🛠️ Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **ML/AI**: scikit-learn, NumPy, PIL
- **Interactive UI**: Streamlit
- **Database**: SQLite (production-ready)
- **Deployment**: Docker, Nginx, GitHub Actions CI/CD

## 📱 Responsive Design

The application is fully responsive and optimized for:
- 📱 Mobile devices (320px+)
- 📱 Large mobile (576px+)
- 📱 Tablets (768px+)
- 💻 Desktops (992px+)
- 🖥️ Large screens (1200px+)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/fashion-recommender.git
   cd fashion-recommender
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   # Start Flask app
   python app_simple.py
   
   # In another terminal, start Streamlit
   streamlit run main_simple.py
   ```

5. **Access the application**
   - Flask app: http://localhost:5001
   - Streamlit app: http://localhost:8501

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

2. **Access the application**
   - Main app: http://localhost:5001
   - Streamlit: http://localhost:8501

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
FLASK_ENV=production
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///fashion.db
```

### Database Setup

The application will automatically create the database and tables on first run. A default admin user is created:
- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change the default admin password in production!

## 📁 Project Structure

```
fashion-recommender/
├── app_simple.py          # Main Flask application
├── main_simple.py         # Streamlit interface
├── models.py              # Database models
├── recommender.py         # ML recommendation engine
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── nginx.conf             # Nginx reverse proxy config
├── deploy.sh              # VPS deployment script
├── .github/
│   └── workflows/
│       └── deploy.yml     # CI/CD pipeline
├── static/                # Static files
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/
├── templates/             # HTML templates
└── instance/              # Database files
```

## 🚀 Deployment

### VPS Deployment

1. **Prepare your VPS**
   ```bash
   # Run the deployment script
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Configure DNS**
   - Point `fashion.dreamware.lk` to your VPS IP
   - Add A record: `fashion.dreamware.lk` → `YOUR_VPS_IP`

3. **Deploy via GitHub Actions**
   - Push to main branch
   - GitHub Actions will automatically deploy

### Manual Deployment

1. **Clone repository on VPS**
   ```bash
   git clone https://github.com/yourusername/fashion-recommender.git
   cd fashion-recommender
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

## 🔒 Security Features

- **CSRF Protection**: Flask-WTF CSRF tokens
- **SQL Injection Prevention**: SQLAlchemy ORM
- **XSS Protection**: Content Security Policy headers
- **Rate Limiting**: Nginx rate limiting
- **Secure Headers**: Security headers via Nginx
- **File Upload Validation**: Allowed file types and size limits

## 📊 Performance

- **Caching**: Static file caching with Nginx
- **Compression**: Gzip compression enabled
- **CDN Ready**: Static assets optimized for CDN
- **Database Optimization**: Indexed queries and efficient relationships
- **Image Optimization**: Automatic image resizing and compression

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/fashion-recommender/issues) page
2. Create a new issue with detailed information
3. Contact: [your-email@example.com](mailto:your-email@example.com)

## 🙏 Acknowledgments

- Bootstrap for the responsive UI framework
- Streamlit for the interactive recommendation interface
- Flask community for the excellent web framework
- All contributors and users of this project

---

**Made with ❤️ for sustainable fashion**
