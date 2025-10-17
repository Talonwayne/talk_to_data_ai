import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ChartGenerator:
    def __init__(self):
        self.chart_types = {
            "bar": self._create_bar_chart,
            "line": self._create_line_chart,
            "pie": self._create_pie_chart,
            "scatter": self._create_scatter_chart,
            "table": self._create_table_chart
        }
    
    def analyze_data(self, data: List[Dict], columns: List[str], data_types: Dict[str, str]) -> Dict[str, Any]:
        """Analyze data to determine the best visualization type"""
        if not data:
            return {"recommended_chart": "table", "reason": "No data available"}
        
        df = pd.DataFrame(data)
        
        # Count column types
        numeric_cols = []
        categorical_cols = []
        datetime_cols = []
        
        for col in columns:
            if col in data_types:
                dtype = data_types[col].lower()
                if 'int' in dtype or 'float' in dtype or 'numeric' in dtype:
                    numeric_cols.append(col)
                elif 'date' in dtype or 'time' in dtype:
                    datetime_cols.append(col)
                else:
                    categorical_cols.append(col)
        
        # Determine best chart type based on data characteristics
        if len(columns) == 2:
            if len(numeric_cols) == 2:
                return {"recommended_chart": "scatter", "reason": "Two numeric columns for correlation analysis"}
            elif len(categorical_cols) == 1 and len(numeric_cols) == 1:
                return {"recommended_chart": "bar", "reason": "Categorical vs numeric data"}
            elif len(categorical_cols) == 2:
                return {"recommended_chart": "table", "reason": "Two categorical columns"}
        
        elif len(columns) == 1:
            if len(numeric_cols) == 1:
                return {"recommended_chart": "bar", "reason": "Single numeric column"}
            else:
                return {"recommended_chart": "pie", "reason": "Single categorical column"}
        
        elif len(datetime_cols) >= 1 and len(numeric_cols) >= 1:
            return {"recommended_chart": "line", "reason": "Time series data detected"}
        
        elif len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            return {"recommended_chart": "bar", "reason": "Categorical and numeric data"}
        
        else:
            return {"recommended_chart": "table", "reason": "Complex data structure"}
    
    def generate_chart(self, data: List[Dict], columns: List[str], data_types: Dict[str, str], 
                      chart_type: Optional[str] = None, title: str = "Data Visualization") -> Dict[str, Any]:
        """Generate a chart based on data and specified type"""
        if not data:
            return {"error": "No data available for visualization"}
        
        # Analyze data if no chart type specified
        if not chart_type:
            analysis = self.analyze_data(data, columns, data_types)
            chart_type = analysis["recommended_chart"]
        
        try:
            if chart_type in self.chart_types:
                chart_func = self.chart_types[chart_type]
                fig = chart_func(data, columns, data_types, title)
                
                return {
                    "success": True,
                    "chart_type": chart_type,
                    "chart_data": fig.to_json(),
                    "title": title
                }
            else:
                return {"error": f"Unsupported chart type: {chart_type}"}
                
        except Exception as e:
            logger.error(f"Chart generation failed: {e}")
            return {"error": f"Failed to generate chart: {str(e)}"}
    
    def _create_bar_chart(self, data: List[Dict], columns: List[str], data_types: Dict[str, str], title: str) -> go.Figure:
        """Create a bar chart"""
        df = pd.DataFrame(data)
        
        # Find categorical and numeric columns
        categorical_col = None
        numeric_col = None
        
        for col in columns:
            if col in data_types:
                dtype = data_types[col].lower()
                if 'int' in dtype or 'float' in dtype or 'numeric' in dtype:
                    numeric_col = col
                else:
                    categorical_col = col
        
        if categorical_col and numeric_col:
            # Group by categorical column and sum numeric column
            grouped = df.groupby(categorical_col)[numeric_col].sum().reset_index()
            fig = px.bar(grouped, x=categorical_col, y=numeric_col, title=title)
        else:
            # Simple bar chart of first column
            first_col = columns[0]
            value_counts = df[first_col].value_counts().reset_index()
            value_counts.columns = [first_col, 'count']
            fig = px.bar(value_counts, x=first_col, y='count', title=title)
        
        return fig
    
    def _create_line_chart(self, data: List[Dict], columns: List[str], data_types: Dict[str, str], title: str) -> go.Figure:
        """Create a line chart"""
        df = pd.DataFrame(data)
        
        # Find datetime and numeric columns
        datetime_col = None
        numeric_col = None
        
        for col in columns:
            if col in data_types:
                dtype = data_types[col].lower()
                if 'date' in dtype or 'time' in dtype:
                    datetime_col = col
                elif 'int' in dtype or 'float' in dtype or 'numeric' in dtype:
                    numeric_col = col
        
        if datetime_col and numeric_col:
            # Convert datetime column
            df[datetime_col] = pd.to_datetime(df[datetime_col])
            df = df.sort_values(datetime_col)
            fig = px.line(df, x=datetime_col, y=numeric_col, title=title)
        else:
            # Simple line chart of first numeric column
            numeric_cols = [col for col in columns if col in data_types and 
                          any(t in data_types[col].lower() for t in ['int', 'float', 'numeric'])]
            if numeric_cols:
                fig = px.line(df, y=numeric_cols[0], title=title)
            else:
                # Fallback to first column
                fig = px.line(df, y=columns[0], title=title)
        
        return fig
    
    def _create_pie_chart(self, data: List[Dict], columns: List[str], data_types: Dict[str, str], title: str) -> go.Figure:
        """Create a pie chart"""
        df = pd.DataFrame(data)
        
        # Use first categorical column
        categorical_col = None
        for col in columns:
            if col in data_types:
                dtype = data_types[col].lower()
                if not ('int' in dtype or 'float' in dtype or 'numeric' in dtype or 'date' in dtype or 'time' in dtype):
                    categorical_col = col
                    break
        
        if not categorical_col:
            categorical_col = columns[0]
        
        # Count values
        value_counts = df[categorical_col].value_counts().reset_index()
        value_counts.columns = ['labels', 'values']
        
        fig = px.pie(value_counts, values='values', names='labels', title=title)
        return fig
    
    def _create_scatter_chart(self, data: List[Dict], columns: List[str], data_types: Dict[str, str], title: str) -> go.Figure:
        """Create a scatter plot"""
        df = pd.DataFrame(data)
        
        # Find numeric columns
        numeric_cols = []
        for col in columns:
            if col in data_types:
                dtype = data_types[col].lower()
                if 'int' in dtype or 'float' in dtype or 'numeric' in dtype:
                    numeric_cols.append(col)
        
        if len(numeric_cols) >= 2:
            fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=title)
        else:
            # Use first two columns
            fig = px.scatter(df, x=columns[0], y=columns[1], title=title)
        
        return fig
    
    def _create_table_chart(self, data: List[Dict], columns: List[str], data_types: Dict[str, str], title: str) -> go.Figure:
        """Create a table visualization"""
        df = pd.DataFrame(data)
        
        fig = go.Figure(data=[go.Table(
            header=dict(values=columns,
                       fill_color='paleturquoise',
                       align='left'),
            cells=dict(values=[df[col].tolist() for col in columns],
                      fill_color='lavender',
                      align='left'))
        ])
        
        fig.update_layout(title=title)
        return fig
