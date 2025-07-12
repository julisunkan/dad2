# Advanced Data Analysis Platform

## Overview

This is a Flask-based web application for data analysis that allows users to upload, clean, analyze, and visualize data through an interactive dashboard. The application provides a complete data analysis workflow from file upload to generating interactive charts and exporting results.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology**: HTML templates with Bootstrap 5 (dark theme)
- **Interactive Elements**: Plotly.js for interactive charts and visualizations
- **Styling**: Custom CSS with CSS variables for theming
- **JavaScript**: Vanilla JavaScript for UI interactions and chart management
- **Theme Support**: Dark/light theme toggle with localStorage persistence

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Session Management**: Flask sessions with configurable secret key
- **File Handling**: Werkzeug for secure file uploads
- **Middleware**: ProxyFix for handling proxy headers
- **Logging**: Python's built-in logging with DEBUG level

### Data Processing Pipeline
- **Data Loading**: Pandas for CSV/Excel file processing with multiple encoding support
- **Data Cleaning**: Custom DataProcessor class for handling missing values, duplicates, and outliers
- **Analytics**: Integration with scikit-learn for outlier detection using Isolation Forest
- **Visualization**: Plotly for generating interactive charts (bar, line, pie, scatter, box, histogram)

## Key Components

### 1. Core Application (`app.py`, `main.py`)
- Flask application initialization with configuration
- Upload/export folder management
- Session configuration and security settings
- Development server setup

### 2. Data Processing (`data_processor.py`)
- **DataProcessor class**: Handles data loading with multiple encoding fallback
- **File Support**: CSV and Excel formats
- **Data Validation**: Empty dataframe checking and size limiting (100K rows)
- **Analytics**: Basic data profiling and quality assessment

### 3. Chart Generation (`chart_generator.py`)
- **ChartGenerator class**: Creates interactive Plotly charts
- **Chart Types**: Bar, line, pie, scatter, box plot, histogram
- **Data Validation**: Column existence and data cleaning before visualization
- **Error Handling**: Comprehensive logging and graceful failure handling

### 4. Export Functionality (`export_handler.py`)
- **ExportHandler class**: Handles data export in multiple formats
- **Export Formats**: CSV, Excel (XLSX), JSON
- **Summary Reports**: Comprehensive analytics reports with data quality metrics
- **File Management**: Automatic filename generation and path handling

### 5. Web Routes (`routes.py`)
- **File Upload**: Secure file handling with UUID-based naming
- **Data Preview**: Table display with pagination and summary statistics
- **Data Cleaning**: Interface for handling missing values and duplicates
- **Analytics Dashboard**: Interactive charts and statistical analysis
- **Export Endpoints**: Download functionality for processed data

### 6. Frontend Templates
- **Base Template**: Consistent navigation and Bootstrap integration
- **Upload Interface**: Drag-and-drop file upload with progress indication
- **Data Preview**: Tabular data display with summary cards
- **Cleaning Interface**: Data quality overview and cleaning options
- **Dashboard**: Analytics visualization with interactive charts

## Data Flow

1. **Upload Phase**: User uploads CSV/Excel file → File validation → Secure storage with UUID
2. **Processing Phase**: Data loading with encoding detection → Basic validation and profiling
3. **Preview Phase**: Display data sample → Show basic statistics → Identify data quality issues
4. **Cleaning Phase**: Handle missing values → Remove duplicates → Detect outliers
5. **Analysis Phase**: Generate descriptive statistics → Create interactive visualizations
6. **Export Phase**: Package results → Multiple format options → Download generation

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualization library
- **Scikit-learn**: Machine learning utilities (Isolation Forest for outlier detection)
- **OpenPyXL**: Excel file handling
- **Werkzeug**: WSGI utilities and security

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme support
- **Font Awesome**: Icon library
- **Plotly.js**: Client-side chart rendering

### File Format Support
- **CSV**: Multiple encoding support (UTF-8, Latin-1, ISO-8859-1, CP1252)
- **Excel**: .xlsx and .xls formats via pandas and openpyxl

## Deployment Strategy

### Development Setup
- **Server**: Flask development server on port 5000
- **Debug Mode**: Enabled for development with detailed error logging
- **Host Configuration**: Configured to accept connections from all interfaces (0.0.0.0)

### File Management
- **Upload Directory**: `uploads/` for temporary file storage
- **Export Directory**: `exports/` for generated output files
- **File Limits**: 16MB maximum upload size
- **Security**: UUID-based filenames to prevent conflicts and enhance security

### Session Management
- **Session Storage**: Flask sessions for maintaining user state
- **Security**: Configurable secret key (environment variable recommended for production)
- **File Tracking**: Current file and original filename stored in session

### Logging and Monitoring
- **Log Level**: DEBUG level for comprehensive development logging
- **Error Handling**: Structured exception handling throughout the application
- **User Feedback**: Flash messages for user notifications and error reporting

The application is designed as a monolithic Flask application suitable for development and small-scale deployment, with clear separation of concerns between data processing, visualization, and web interface components.