import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import logging

class ChartGenerator:
    """Generate interactive charts using Plotly"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_chart(self, df, chart_type, x_column, y_column, title="Chart"):
        """Create a chart based on the specified parameters"""
        try:
            if df.empty:
                return None
            
            # Validate columns exist
            if x_column not in df.columns:
                self.logger.error(f"Column {x_column} not found in dataframe")
                return None
            
            if chart_type in ['bar', 'line', 'scatter', 'box'] and y_column and y_column not in df.columns:
                self.logger.error(f"Column {y_column} not found in dataframe")
                return None
            
            # Clean data for visualization
            chart_df = df[[x_column, y_column]].dropna() if y_column else df[[x_column]].dropna()
            
            if chart_df.empty:
                return None
            
            # Generate chart based on type
            if chart_type == 'bar':
                fig = self._create_bar_chart(chart_df, x_column, y_column, title)
            elif chart_type == 'line':
                fig = self._create_line_chart(chart_df, x_column, y_column, title)
            elif chart_type == 'pie':
                fig = self._create_pie_chart(chart_df, x_column, title)
            elif chart_type == 'scatter':
                fig = self._create_scatter_chart(chart_df, x_column, y_column, title)
            elif chart_type == 'box':
                fig = self._create_box_chart(chart_df, x_column, y_column, title)
            elif chart_type == 'histogram':
                fig = self._create_histogram(chart_df, x_column, title)
            else:
                self.logger.error(f"Unsupported chart type: {chart_type}")
                return None
            
            if fig:
                # Apply colorful theme for better visibility
                fig.update_layout(
                    template="plotly_white",
                    paper_bgcolor='rgba(248,249,250,0.9)',
                    plot_bgcolor='rgba(255,255,255,0.9)',
                    font=dict(color='#495057', size=12),
                    title_font_size=16,
                    height=400,
                    margin=dict(l=40, r=40, t=50, b=40),
                    showlegend=True,
                    legend=dict(
                        bgcolor='rgba(255,255,255,0.8)',
                        bordercolor='rgba(0,0,0,0.1)',
                        borderwidth=1
                    )
                )
                
                return fig.to_html(include_plotlyjs=False, div_id=f"chart_{chart_type}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating chart: {str(e)}")
            return None
    
    def _create_bar_chart(self, df, x_col, y_col, title):
        """Create a bar chart"""
        try:
            # Aggregate data if necessary
            if df[y_col].dtype in ['object', 'category']:
                # Count occurrences
                chart_data = df[x_col].value_counts().head(20)
                fig = go.Figure(data=[go.Bar(x=chart_data.index, y=chart_data.values)])
            else:
                # Group by x_col and sum/mean y_col
                if df[x_col].dtype in ['object', 'category']:
                    chart_data = df.groupby(x_col)[y_col].sum().head(20)
                    fig = go.Figure(data=[go.Bar(x=chart_data.index, y=chart_data.values)])
                else:
                    # For numeric x, create bins
                    fig = px.bar(df.head(50), x=x_col, y=y_col)
            
            fig.update_layout(title=title, xaxis_title=x_col, yaxis_title=y_col)
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating bar chart: {str(e)}")
            return None
    
    def _create_line_chart(self, df, x_col, y_col, title):
        """Create a line chart"""
        try:
            # Sort by x column for better line visualization
            df_sorted = df.sort_values(x_col)
            
            # Limit data points for performance
            if len(df_sorted) > 1000:
                df_sorted = df_sorted.iloc[::len(df_sorted)//1000]
            
            fig = go.Figure(data=[go.Scatter(
                x=df_sorted[x_col], 
                y=df_sorted[y_col],
                mode='lines+markers',
                line=dict(width=2),
                marker=dict(size=4)
            )])
            
            fig.update_layout(title=title, xaxis_title=x_col, yaxis_title=y_col)
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating line chart: {str(e)}")
            return None
    
    def _create_pie_chart(self, df, x_col, title):
        """Create a pie chart"""
        try:
            # Get value counts for the column
            value_counts = df[x_col].value_counts().head(10)  # Limit to top 10
            
            fig = go.Figure(data=[go.Pie(
                labels=value_counts.index,
                values=value_counts.values,
                hole=0.3
            )])
            
            fig.update_layout(title=title)
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating pie chart: {str(e)}")
            return None
    
    def _create_scatter_chart(self, df, x_col, y_col, title):
        """Create a scatter plot"""
        try:
            # Validate input columns
            if not x_col or not y_col or x_col not in df.columns or y_col not in df.columns:
                self.logger.error(f"Invalid columns for scatter plot: x_col='{x_col}', y_col='{y_col}'")
                return None
            
            # Limit data points for performance
            plot_df = df.head(1000)
            
            fig = go.Figure(data=[go.Scatter(
                x=plot_df[x_col],
                y=plot_df[y_col],
                mode='markers',
                marker=dict(
                    size=6,
                    opacity=0.7,
                    color=plot_df[y_col] if plot_df[y_col].dtype in ['int64', 'float64'] else None,
                    colorscale='Viridis',
                    showscale=True if plot_df[y_col].dtype in ['int64', 'float64'] else False
                )
            )])
            
            fig.update_layout(title=title, xaxis_title=x_col, yaxis_title=y_col)
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating scatter chart: {str(e)}")
            return None
    
    def _create_box_chart(self, df, x_col, y_col, title):
        """Create a box plot"""
        try:
            if df[x_col].dtype in ['object', 'category']:
                # Box plot by category
                fig = px.box(df, x=x_col, y=y_col)
            else:
                # Single box plot for numeric data
                fig = go.Figure(data=[go.Box(y=df[y_col], name=y_col)])
            
            fig.update_layout(title=title, xaxis_title=x_col, yaxis_title=y_col)
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating box chart: {str(e)}")
            return None
    
    def _create_histogram(self, df, x_col, title):
        """Create a histogram"""
        try:
            fig = go.Figure(data=[go.Histogram(
                x=df[x_col],
                nbinsx=min(50, len(df[x_col].unique()))
            )])
            
            fig.update_layout(title=title, xaxis_title=x_col, yaxis_title='Frequency')
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating histogram: {str(e)}")
            return None
    
    def generate_automatic_charts(self, df):
        """Generate relevant charts automatically based on data characteristics"""
        try:
            auto_charts = []
            
            # Get numeric and categorical columns
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            # Chart 1: Distribution of first numeric column (histogram)
            if numeric_cols:
                first_numeric = numeric_cols[0]
                chart_html = self.create_chart(df, 'histogram', first_numeric, None, 
                                               f'Distribution of {first_numeric}')
                if chart_html:
                    auto_charts.append({
                        'title': f'Distribution of {first_numeric}',
                        'type': 'histogram',
                        'html': chart_html
                    })
                else:
                    # Add error message if chart failed
                    auto_charts.append({
                        'title': f'Distribution of {first_numeric}',
                        'type': 'error',
                        'html': self._create_error_message(f'Unable to generate histogram for {first_numeric}')
                    })
            
            # Chart 2: Top categories if categorical data exists
            if categorical_cols:
                first_categorical = categorical_cols[0]
                chart_html = self.create_chart(df, 'pie', first_categorical, None, 
                                               f'Distribution of {first_categorical}')
                if chart_html:
                    auto_charts.append({
                        'title': f'Distribution of {first_categorical}',
                        'type': 'pie',
                        'html': chart_html
                    })
                else:
                    # Add error message if chart failed
                    auto_charts.append({
                        'title': f'Distribution of {first_categorical}',
                        'type': 'error',
                        'html': self._create_error_message(f'Unable to generate pie chart for {first_categorical}')
                    })
            
            # Chart 3: Correlation scatter plot (if we have 2+ numeric columns)
            if len(numeric_cols) >= 2:
                chart_html = self.create_chart(df, 'scatter', numeric_cols[0], numeric_cols[1], 
                                               f'{numeric_cols[0]} vs {numeric_cols[1]}')
                if chart_html:
                    auto_charts.append({
                        'title': f'{numeric_cols[0]} vs {numeric_cols[1]}',
                        'type': 'scatter',
                        'html': chart_html
                    })
                else:
                    # Add error message if chart failed
                    auto_charts.append({
                        'title': f'{numeric_cols[0]} vs {numeric_cols[1]}',
                        'type': 'error',
                        'html': self._create_error_message(f'Unable to generate scatter plot for {numeric_cols[0]} vs {numeric_cols[1]}')
                    })
            
            # Chart 4: Bar chart of categorical vs numeric (if both exist)
            if categorical_cols and numeric_cols:
                # Use first categorical and first numeric
                chart_html = self.create_chart(df, 'bar', categorical_cols[0], numeric_cols[0], 
                                               f'{numeric_cols[0]} by {categorical_cols[0]}')
                if chart_html:
                    auto_charts.append({
                        'title': f'{numeric_cols[0]} by {categorical_cols[0]}',
                        'type': 'bar',
                        'html': chart_html
                    })
                else:
                    # Add error message if chart failed
                    auto_charts.append({
                        'title': f'{numeric_cols[0]} by {categorical_cols[0]}',
                        'type': 'error',
                        'html': self._create_error_message(f'Unable to generate bar chart for {numeric_cols[0]} by {categorical_cols[0]}')
                    })
            
            # If no charts were generated, show a helpful message
            if not auto_charts:
                auto_charts.append({
                    'title': 'No Charts Available',
                    'type': 'info',
                    'html': self._create_info_message('No suitable data found for automatic chart generation. Please ensure your data has numeric or categorical columns.')
                })
            
            return auto_charts
            
        except Exception as e:
            self.logger.error(f"Error generating automatic charts: {str(e)}")
            return [{
                'title': 'Chart Generation Error',
                'type': 'error',
                'html': self._create_error_message(f'An error occurred while generating charts: {str(e)}')
            }]
    
    def _create_error_message(self, message):
        """Create an error message HTML"""
        return f"""
        <div class="alert alert-danger d-flex align-items-center" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <div>
                <strong>Chart Generation Failed:</strong> {message}
                <br><small>Please check your data or try a different visualization.</small>
            </div>
        </div>
        """
    
    def _create_info_message(self, message):
        """Create an info message HTML"""
        return f"""
        <div class="alert alert-info d-flex align-items-center" role="alert">
            <i class="fas fa-info-circle me-2"></i>
            <div>
                <strong>Information:</strong> {message}
            </div>
        </div>
        """
