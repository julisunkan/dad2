import os
import pandas as pd
from app import app
import logging

class ExportHandler:
    """Handle data export in various formats"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def export_data(self, df, format_type, original_filename):
        """Export dataframe in specified format"""
        try:
            # Generate export filename
            base_name = os.path.splitext(original_filename)[0]
            export_filename = f"export_{base_name}_{format_type}.{format_type}"
            export_path = os.path.join(app.config['EXPORT_FOLDER'], export_filename)
            
            if format_type == 'csv':
                df.to_csv(export_path, index=False)
            elif format_type == 'xlsx':
                df.to_excel(export_path, index=False, engine='openpyxl')
            elif format_type == 'json':
                df.to_json(export_path, orient='records', indent=2)
            else:
                self.logger.error(f"Unsupported export format: {format_type}")
                return None
            
            self.logger.info(f"Data exported to {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {str(e)}")
            return None
    
    def export_summary_report(self, df, analytics, format_type, original_filename):
        """Export a comprehensive summary report"""
        try:
            # Create summary dataframe
            summary_data = {
                'Metric': [
                    'Total Rows',
                    'Total Columns',
                    'Missing Values',
                    'Numeric Columns',
                    'Categorical Columns',
                    'Data Quality Score'
                ],
                'Value': [
                    len(df),
                    len(df.columns),
                    int(df.isnull().sum().sum()),
                    len(df.select_dtypes(include=['number']).columns),
                    len(df.select_dtypes(include=['object']).columns),
                    analytics.get('prescriptive', {}).get('data_quality_score', 'N/A')
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            
            # Generate export filename
            base_name = os.path.splitext(original_filename)[0]
            export_filename = f"summary_report_{base_name}.{format_type}"
            export_path = os.path.join(app.config['EXPORT_FOLDER'], export_filename)
            
            if format_type == 'csv':
                summary_df.to_csv(export_path, index=False)
            elif format_type == 'xlsx':
                with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Add descriptive statistics if available
                    if not df.empty:
                        desc_stats = df.describe()
                        if not desc_stats.empty:
                            desc_stats.to_excel(writer, sheet_name='Descriptive_Stats')
            
            self.logger.info(f"Summary report exported to {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Error exporting summary report: {str(e)}")
            return None
