import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import logging

class DataProcessor:
    """Handle data loading, cleaning, and analysis operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_data(self, filepath):
        """Load data from CSV or Excel file"""
        try:
            if filepath.endswith('.csv'):
                # Try different encodings
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(filepath, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    self.logger.error(f"Could not decode CSV file with any encoding")
                    return None
            else:
                df = pd.read_excel(filepath)
            
            # Basic validation
            if df.empty:
                self.logger.error("Loaded dataframe is empty")
                return None
            
            # Limit to reasonable size for demo (adjust as needed)
            if len(df) > 100000:
                self.logger.warning(f"Large dataset ({len(df)} rows), taking first 100,000 rows")
                df = df.head(100000)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            return None
    
    def get_data_info(self, df):
        """Get basic information about the dataset"""
        try:
            info = {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'numeric_columns': list(df.select_dtypes(include=[np.number]).columns),
                'categorical_columns': list(df.select_dtypes(include=['object']).columns),
                'missing_values': df.isnull().sum().to_dict()
            }
            return info
        except Exception as e:
            self.logger.error(f"Error getting data info: {str(e)}")
            return {}
    
    def analyze_data_quality(self, df):
        """Analyze data quality issues"""
        try:
            analysis = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': {},
                'duplicates': df.duplicated().sum(),
                'data_types': df.dtypes.to_dict(),
                'outliers': {},
                'memory_usage': df.memory_usage(deep=True).sum()
            }
            
            # Analyze missing values
            for col in df.columns:
                missing_count = df[col].isnull().sum()
                if missing_count > 0:
                    analysis['missing_values'][col] = {
                        'count': int(missing_count),
                        'percentage': round((missing_count / len(df)) * 100, 2)
                    }
            
            # Analyze outliers for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                try:
                    if df[col].notna().sum() > 10:  # Need at least 10 non-null values
                        Q1 = df[col].quantile(0.25)
                        Q3 = df[col].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
                        if len(outliers) > 0:
                            analysis['outliers'][col] = int(len(outliers))
                except Exception:
                    continue
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing data quality: {str(e)}")
            return {}
    
    def clean_data(self, df, operations):
        """Apply data cleaning operations"""
        try:
            cleaned_df = df.copy()
            
            # Remove duplicates
            if operations.get('remove_duplicates', False):
                initial_rows = len(cleaned_df)
                cleaned_df = cleaned_df.drop_duplicates()
                self.logger.info(f"Removed {initial_rows - len(cleaned_df)} duplicate rows")
            
            # Handle missing values
            missing_strategy = operations.get('handle_missing', 'drop')
            if missing_strategy == 'drop':
                cleaned_df = cleaned_df.dropna()
            elif missing_strategy == 'fill_mean':
                numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    cleaned_df[col].fillna(cleaned_df[col].mean(), inplace=True)
            elif missing_strategy == 'fill_median':
                numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    cleaned_df[col].fillna(cleaned_df[col].median(), inplace=True)
            elif missing_strategy == 'fill_mode':
                for col in cleaned_df.columns:
                    if cleaned_df[col].mode().empty:
                        continue
                    mode_value = cleaned_df[col].mode()[0]
                    cleaned_df[col].fillna(mode_value, inplace=True)
            
            # Remove outliers using Isolation Forest
            if operations.get('remove_outliers', False):
                numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0 and len(cleaned_df) > 10:
                    try:
                        isolation_forest = IsolationForest(contamination=0.1, random_state=42)
                        outliers = isolation_forest.fit_predict(cleaned_df[numeric_cols].fillna(0))
                        cleaned_df = cleaned_df[outliers == 1]
                        self.logger.info(f"Removed outliers, rows remaining: {len(cleaned_df)}")
                    except Exception as e:
                        self.logger.warning(f"Could not remove outliers: {str(e)}")
            
            # Correct data types
            if operations.get('correct_dtypes', False):
                cleaned_df = self._correct_data_types(cleaned_df)
            
            return cleaned_df
            
        except Exception as e:
            self.logger.error(f"Error cleaning data: {str(e)}")
            return None
    
    def _correct_data_types(self, df):
        """Attempt to correct data types automatically"""
        try:
            corrected_df = df.copy()
            
            for col in corrected_df.columns:
                # Try to convert to numeric if possible
                if corrected_df[col].dtype == 'object':
                    try:
                        # Check if it's mostly numeric
                        numeric_converted = pd.to_numeric(corrected_df[col], errors='coerce')
                        if numeric_converted.notna().sum() / len(corrected_df[col]) > 0.8:
                            corrected_df[col] = numeric_converted
                            continue
                    except Exception:
                        pass
                    
                    # Try to convert to datetime
                    try:
                        datetime_converted = pd.to_datetime(corrected_df[col], errors='coerce')
                        if datetime_converted.notna().sum() / len(corrected_df[col]) > 0.8:
                            corrected_df[col] = datetime_converted
                            continue
                    except Exception:
                        pass
            
            return corrected_df
            
        except Exception as e:
            self.logger.error(f"Error correcting data types: {str(e)}")
            return df
    
    def get_analytics(self, df):
        """Generate comprehensive analytics for the dataset"""
        try:
            analytics = {
                'descriptive': self._get_descriptive_analytics(df),
                'diagnostic': self._get_diagnostic_analytics(df),
                'predictive': self._get_predictive_analytics(df),
                'prescriptive': self._get_prescriptive_analytics(df)
            }
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error generating analytics: {str(e)}")
            return {}
    
    def _get_descriptive_analytics(self, df):
        """Get descriptive statistics"""
        try:
            desc = {
                'basic_stats': df.describe().to_dict() if not df.empty else {},
                'correlation_matrix': {},
                'data_profile': {
                    'total_rows': len(df),
                    'total_columns': len(df.columns),
                    'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
                    'categorical_columns': len(df.select_dtypes(include=['object']).columns),
                    'missing_values_total': int(df.isnull().sum().sum())
                }
            }
            
            # Correlation matrix for numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) > 1:
                desc['correlation_matrix'] = numeric_df.corr().to_dict()
            
            return desc
            
        except Exception as e:
            self.logger.error(f"Error in descriptive analytics: {str(e)}")
            return {}
    
    def _get_diagnostic_analytics(self, df):
        """Get diagnostic analytics"""
        try:
            diag = {
                'value_counts': {},
                'group_analysis': {},
                'distribution_analysis': {}
            }
            
            # Value counts for categorical columns (top 10)
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols[:5]:  # Limit to first 5 categorical columns
                if df[col].notna().sum() > 0:
                    diag['value_counts'][col] = df[col].value_counts().head(10).to_dict()
            
            # Distribution analysis for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
                if df[col].notna().sum() > 0:
                    diag['distribution_analysis'][col] = {
                        'mean': float(df[col].mean()),
                        'median': float(df[col].median()),
                        'std': float(df[col].std()),
                        'skewness': float(df[col].skew()) if hasattr(df[col], 'skew') else 0
                    }
            
            return diag
            
        except Exception as e:
            self.logger.error(f"Error in diagnostic analytics: {str(e)}")
            return {}
    
    def _get_predictive_analytics(self, df):
        """Get predictive analytics (simplified)"""
        try:
            pred = {
                'trends': {},
                'patterns': {},
                'forecast_summary': 'Trend analysis available for time-series data'
            }
            
            # Simple trend analysis for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                if df[col].notna().sum() > 5:
                    values = df[col].dropna().values
                    if len(values) > 1:
                        trend = 'increasing' if values[-1] > values[0] else 'decreasing'
                        pred['trends'][col] = {
                            'direction': trend,
                            'change_percentage': float(((values[-1] - values[0]) / values[0]) * 100) if values[0] != 0 else 0
                        }
            
            return pred
            
        except Exception as e:
            self.logger.error(f"Error in predictive analytics: {str(e)}")
            return {}
    
    def _get_prescriptive_analytics(self, df):
        """Get prescriptive analytics recommendations"""
        try:
            presc = {
                'recommendations': [],
                'data_quality_score': 0,
                'optimization_suggestions': []
            }
            
            # Calculate data quality score
            total_cells = df.shape[0] * df.shape[1]
            missing_cells = df.isnull().sum().sum()
            quality_score = ((total_cells - missing_cells) / total_cells) * 100 if total_cells > 0 else 0
            presc['data_quality_score'] = round(quality_score, 2)
            
            # Generate recommendations
            if missing_cells > 0:
                presc['recommendations'].append(f"Consider handling {missing_cells} missing values")
            
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                presc['recommendations'].append(f"Remove {duplicates} duplicate rows")
            
            # Optimization suggestions
            if len(df.columns) > 50:
                presc['optimization_suggestions'].append("Consider feature selection for large number of columns")
            
            if len(df) > 10000:
                presc['optimization_suggestions'].append("Consider data sampling for better performance")
            
            return presc
            
        except Exception as e:
            self.logger.error(f"Error in prescriptive analytics: {str(e)}")
            return {}
