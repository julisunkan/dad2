import os
import uuid
from flask import render_template, request, redirect, url_for, flash, session, send_file, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
from app import app
from data_processor import DataProcessor
from chart_generator import ChartGenerator
from export_handler import ExportHandler

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Landing page with overview of features"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file upload and initial data loading"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Generate unique filename
                filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Store file info in session
                session['current_file'] = filename
                session['original_filename'] = file.filename
                
                # Load and validate data
                processor = DataProcessor()
                df = processor.load_data(filepath)
                
                if df is not None:
                    session['data_shape'] = df.shape
                    flash(f'File uploaded successfully! Dataset contains {df.shape[0]} rows and {df.shape[1]} columns.', 'success')
                    return redirect(url_for('preview_data'))
                else:
                    flash('Error loading file. Please check the file format.', 'error')
                    
            except Exception as e:
                app.logger.error(f"Upload error: {str(e)}")
                flash(f'Error uploading file: {str(e)}', 'error')
        else:
            flash('Invalid file type. Please upload CSV or Excel files only.', 'error')
    
    return render_template('upload.html')

@app.route('/preview')
def preview_data():
    """Preview uploaded data with pagination"""
    if 'current_file' not in session:
        flash('No file uploaded. Please upload a file first.', 'warning')
        return redirect(url_for('upload_file'))
    
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['current_file'])
        processor = DataProcessor()
        df = processor.load_data(filepath)
        
        if df is None:
            flash('Error loading data file.', 'error')
            return redirect(url_for('upload_file'))
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 50
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Get data subset
        data_subset = df.iloc[start_idx:end_idx]
        
        # Calculate pagination info
        total_pages = (len(df) + per_page - 1) // per_page
        
        # Get basic data info
        data_info = processor.get_data_info(df)
        
        return render_template('preview.html', 
                             data=data_subset.to_dict('records'),
                             columns=df.columns.tolist(),
                             current_page=page,
                             total_pages=total_pages,
                             total_rows=len(df),
                             data_info=data_info)
        
    except Exception as e:
        app.logger.error(f"Preview error: {str(e)}")
        flash(f'Error previewing data: {str(e)}', 'error')
        return redirect(url_for('upload_file'))

@app.route('/cleaning')
def data_cleaning():
    """Data cleaning interface"""
    if 'current_file' not in session:
        flash('No file uploaded. Please upload a file first.', 'warning')
        return redirect(url_for('upload_file'))
    
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['current_file'])
        processor = DataProcessor()
        df = processor.load_data(filepath)
        
        if df is None:
            flash('Error loading data file.', 'error')
            return redirect(url_for('upload_file'))
        
        # Get cleaning analysis
        cleaning_info = processor.analyze_data_quality(df)
        
        return render_template('cleaning.html', 
                             cleaning_info=cleaning_info,
                             columns=df.columns.tolist())
        
    except Exception as e:
        app.logger.error(f"Cleaning error: {str(e)}")
        flash(f'Error analyzing data: {str(e)}', 'error')
        return redirect(url_for('upload_file'))

@app.route('/clean_data', methods=['POST'])
def clean_data():
    """Apply data cleaning operations"""
    if 'current_file' not in session:
        flash('No file uploaded. Please upload a file first.', 'warning')
        return redirect(url_for('upload_file'))
    
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['current_file'])
        processor = DataProcessor()
        df = processor.load_data(filepath)
        
        if df is None:
            flash('Error loading data file.', 'error')
            return redirect(url_for('upload_file'))
        
        # Get cleaning options from form
        operations = {
            'remove_duplicates': 'remove_duplicates' in request.form,
            'handle_missing': request.form.get('missing_strategy', 'drop'),
            'remove_outliers': 'remove_outliers' in request.form,
            'correct_dtypes': 'correct_dtypes' in request.form
        }
        
        # Apply cleaning operations
        cleaned_df = processor.clean_data(df, operations)
        
        if cleaned_df is not None:
            # Save cleaned data
            cleaned_filename = 'cleaned_' + session['current_file']
            cleaned_filepath = os.path.join(app.config['UPLOAD_FOLDER'], cleaned_filename)
            
            if cleaned_filename.endswith('.csv'):
                cleaned_df.to_csv(cleaned_filepath, index=False)
            else:
                cleaned_df.to_excel(cleaned_filepath, index=False)
            
            # Update session with cleaned file
            session['current_file'] = cleaned_filename
            session['data_shape'] = cleaned_df.shape
            
            flash(f'Data cleaned successfully! New dataset: {cleaned_df.shape[0]} rows, {cleaned_df.shape[1]} columns.', 'success')
        else:
            flash('Error cleaning data.', 'error')
        
    except Exception as e:
        app.logger.error(f"Data cleaning error: {str(e)}")
        flash(f'Error cleaning data: {str(e)}', 'error')
    
    return redirect(url_for('data_cleaning'))

@app.route('/dashboard')
def dashboard():
    """Main analytics dashboard"""
    if 'current_file' not in session:
        flash('No file uploaded. Please upload a file first.', 'warning')
        return redirect(url_for('upload_file'))
    
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['current_file'])
        processor = DataProcessor()
        df = processor.load_data(filepath)
        
        if df is None:
            flash('Error loading data file.', 'error')
            return redirect(url_for('upload_file'))
        
        # Get analytics data
        analytics = processor.get_analytics(df)
        
        # Get column information for chart generation
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Generate automatic charts
        chart_gen = ChartGenerator()
        auto_charts = chart_gen.generate_automatic_charts(df)
        
        return render_template('dashboard.html',
                             analytics=analytics,
                             numeric_cols=numeric_cols,
                             categorical_cols=categorical_cols,
                             all_cols=df.columns.tolist(),
                             auto_charts=auto_charts)
        
    except Exception as e:
        app.logger.error(f"Dashboard error: {str(e)}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('upload_file'))

@app.route('/generate_chart', methods=['POST'])
def generate_chart():
    """Generate a chart based on user selections"""
    if 'current_file' not in session:
        return jsonify({'error': 'No file uploaded'}), 400
    
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['current_file'])
        processor = DataProcessor()
        df = processor.load_data(filepath)
        
        if df is None:
            return jsonify({'error': 'Error loading data'}), 400
        
        # Get chart parameters
        chart_type = request.form.get('chart_type')
        x_column = request.form.get('x_column')
        y_column = request.form.get('y_column')
        title = request.form.get('title', f'{chart_type.title()} Chart')
        
        # Generate chart
        chart_gen = ChartGenerator()
        chart_html = chart_gen.create_chart(df, chart_type, x_column, y_column, title)
        
        if chart_html:
            return jsonify({'chart_html': chart_html})
        else:
            return jsonify({'error': 'Error generating chart'}), 400
        
    except Exception as e:
        app.logger.error(f"Chart generation error: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/export/<format>')
def export_data(format):
    """Export data in specified format"""
    if 'current_file' not in session:
        flash('No file uploaded. Please upload a file first.', 'warning')
        return redirect(url_for('upload_file'))
    
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['current_file'])
        processor = DataProcessor()
        df = processor.load_data(filepath)
        
        if df is None:
            flash('Error loading data file.', 'error')
            return redirect(url_for('dashboard'))
        
        # Generate export
        export_handler = ExportHandler()
        export_path = export_handler.export_data(df, format, session.get('original_filename', 'data'))
        
        if export_path and os.path.exists(export_path):
            return send_file(export_path, as_attachment=True)
        else:
            flash(f'Error exporting data as {format.upper()}', 'error')
            
    except Exception as e:
        app.logger.error(f"Export error: {str(e)}")
        flash(f'Error exporting data: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('upload_file'))

@app.errorhandler(404)
def not_found(e):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f"Internal error: {str(e)}")
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))
