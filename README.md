# 🏢 Room Allocation System

A comprehensive web application for managing project room and Oasis workspace allocations with advanced analytics, admin controls, and security features.

## 🌟 Features

### Core Functionality
- **Project Room Allocation**: Team-based room allocation with preference management
- **Oasis Workspace Management**: Individual workspace allocation system
- **Intelligent Allocation Algorithms**: Fair distribution based on team size and preferences
- **Real-time Capacity Tracking**: Live monitoring of room and workspace availability

### Advanced Features
- **Analytics Dashboard**: Comprehensive charts and statistics
- **Admin Control Panel**: Full system management capabilities
- **Security Features**: Input validation, rate limiting, and session management
- **Data Export**: CSV export for external analysis
- **Archive System**: Historical data preservation
- **Interactive Matrix**: Attendance confirmation system

### User Interface
- **Modern Design**: Clean, responsive Streamlit interface
- **Intuitive Navigation**: Easy-to-use sidebar navigation
- **Real-time Updates**: Dynamic content updates
- **Mobile Friendly**: Responsive design for all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd room_allocation_system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - Open your browser and navigate to `http://localhost:8501`
   - The application will be ready to use immediately

## 📋 Usage Guide

### For Users

#### Submitting Team Preferences
1. Navigate to "Project Rooms" page
2. Fill in team details:
   - Team name (required)
   - Contact person (required)
   - Team size (3-6 members)
   - Preferred days (Monday & Wednesday OR Tuesday & Thursday)
3. Click "Submit Preference"

#### Submitting Oasis Preferences
1. Navigate to "Oasis Workspace" page
2. Enter your name
3. Select preferred days (up to 5 weekdays)
4. Click "Submit Preference"

#### Viewing Allocations
1. Navigate to "Current Allocations" page
2. View project room assignments
3. View Oasis workspace assignments
4. Use the interactive matrix for attendance confirmation

### For Administrators

#### Admin Access
1. Navigate to "Admin Panel" page
2. Enter admin password: `trainee`
3. Access admin functions

#### Admin Functions
- **Run Allocations**: Execute allocation algorithms
- **Manual Editing**: Modify allocations via interactive grids
- **Bulk Operations**: Delete multiple entries with archiving
- **System Configuration**: Update display texts and settings
- **Data Management**: Reset system for new allocation periods

#### Analytics
1. Navigate to "Analytics" page
2. View comprehensive statistics:
   - System overview and success rates
   - Project room analytics
   - Oasis usage patterns
   - Historical trends
   - Export capabilities

## 🏗️ Architecture

### Project Structure
```
room_allocation_system/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── data/
│   ├── storage.py        # Data storage layer
│   └── models.py         # Data models and validation
├── logic/
│   └── allocation.py     # Allocation algorithms
├── ui/
│   └── components.py     # UI components
├── utils/
│   ├── helpers.py        # Utility functions
│   └── security.py       # Security features
└── storage/              # Data files (auto-created)
    ├── weekly_preferences.json
    ├── oasis_preferences.json
    ├── weekly_allocations.json
    ├── oasis_allocations.json
    ├── admin_settings.json
    └── archive/          # Archived data
```

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with JSON-based storage
- **Charts**: Plotly for interactive visualizations
- **Data Processing**: Pandas for data manipulation
- **Security**: Custom validation and rate limiting

### Key Algorithms

#### Project Room Allocation
1. Separate teams by day preference (Mon/Wed vs Tue/Thu)
2. Sort teams by size (larger teams get priority)
3. Use random shuffling for fairness among same-size teams
4. Attempt preferred day allocation first
5. Fallback to alternative days for unplaced teams
6. Report any teams that couldn't be accommodated

#### Oasis Allocation
1. First pass: Ensure everyone gets at least one preferred day
2. Additional passes: Fill remaining spots with users' other preferences
3. Random assignment order for fairness
4. Continue until no more assignments possible

## 🔒 Security Features

### Input Validation
- Comprehensive sanitization of all user inputs
- Protection against injection attacks
- Length and format validation

### Rate Limiting
- Maximum 5 submissions per minute per user
- Automatic lockout for excessive attempts
- Configurable time windows

### Admin Security
- Password-protected admin functions
- Session timeout management
- Brute force protection with lockout
- Secure session state management

### Data Protection
- Input sanitization
- Archive system for data preservation
- Backup functionality
- Secure data handling

## 🚀 Deployment

### Streamlit Community Cloud (Recommended)

1. **Prepare Repository**
   - Ensure all files are in a Git repository
   - Verify `requirements.txt` is complete
   - Test locally before deployment

2. **Deploy to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select the main branch and `app.py`
   - Click "Deploy"

3. **Configuration**
   - No additional configuration needed
   - Application will be available at your Streamlit Cloud URL

### Local Deployment

1. **Production Setup**
   ```bash
   pip install -r requirements.txt
   streamlit run app.py --server.port 8501 --server.address 0.0.0.0
   ```

2. **Environment Variables** (Optional)
   ```bash
   export STREAMLIT_SERVER_PORT=8501
   export STREAMLIT_SERVER_ADDRESS=0.0.0.0
   ```

### Docker Deployment (Optional)

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and Run**
   ```bash
   docker build -t room-allocation-system .
   docker run -p 8501:8501 room-allocation-system
   ```

## ⚙️ Configuration

### Admin Settings
- **Welcome Text**: Customize home page message
- **Instructions**: Update form instructions
- **Allocation Period**: Set current period name
- **Room Configuration**: Modify available rooms and capacities

### System Configuration
- **Rate Limiting**: Adjust submission limits
- **Session Timeout**: Configure admin session duration
- **Capacity Limits**: Set room and workspace capacities

## 📊 Data Management

### Data Storage
- JSON-based file storage for simplicity and portability
- Automatic backup and archive system
- Data validation and integrity checks

### Data Export
- CSV export for all data types
- Summary reports generation
- Historical data access

### Data Archiving
- Automatic archiving when data is deleted
- Preservation of historical records
- Archive data included in analytics

## 🔧 Troubleshooting

### Common Issues

1. **Application Won't Start**
   - Check Python version (3.11+ required)
   - Verify all dependencies are installed
   - Check for port conflicts

2. **Form Submissions Failing**
   - Verify input validation requirements
   - Check for rate limiting
   - Ensure all required fields are filled

3. **Admin Access Issues**
   - Default password is `trainee`
   - Check for account lockout
   - Clear browser cache if needed

4. **Data Not Saving**
   - Check file permissions in storage directory
   - Verify disk space availability
   - Check for JSON formatting errors

### Performance Optimization
- Regular data archiving to maintain performance
- Periodic cleanup of old session data
- Monitor memory usage for large datasets

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a virtual environment
3. Install dependencies
4. Make changes and test thoroughly
5. Submit pull request

### Code Standards
- Follow PEP 8 Python style guide
- Add docstrings to all functions
- Include error handling
- Write comprehensive tests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section
2. Review the usage guide
3. Check the project documentation
4. Submit an issue on the repository

## 🎯 Future Enhancements

### Planned Features
- Email notifications for allocations
- Calendar integration
- Mobile app version
- Advanced reporting features
- Multi-language support

### Technical Improvements
- Database integration options
- API endpoints for external integration
- Enhanced security features
- Performance optimizations

---

**Built with ❤️ using Streamlit and Python**

