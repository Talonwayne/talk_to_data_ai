# 🗣️ Talk to Your Data

A natural language database query system that allows users to ask questions in plain English and get insights through interactive visualizations. Built with OpenAI GPT-4, FastAPI, React, and Plotly.

## Features

- **Natural Language Queries**: Ask questions in plain English like "Show me total sales by product category"
- **Automatic SQL Generation**: AI converts your questions into optimized SQL queries
- **Interactive Visualizations**: Get charts, graphs, and tables automatically generated from your data
- **Schema Exploration**: Browse your database structure to understand available data
- **Safe Query Execution**: Read-only queries with built-in security protections
- **Real-time Results**: Fast query processing with immediate visual feedback

## Architecture

- **Backend**: Python with FastAPI for API endpoints and OpenAI integration
- **Frontend**: React with Vite for responsive UI
- **Database**: PostgreSQL support with schema introspection
- **AI**: OpenAI GPT-4 with function calling for query interpretation
- **Visualization**: Plotly for interactive charts and graphs

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL database
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd talk_to_data_ai
   ```

2. **Set up the backend**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Set up environment variables
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Start the application**
   ```bash
   # Terminal 1: Start backend
   cd backend
   python main.py

   # Terminal 2: Start frontend
   cd frontend
   npm run dev
   ```

5. **Open your browser**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## Usage

### 1. Connect to Your Database

Enter your PostgreSQL connection string in the format:
```
postgresql://username:password@host:port/database_name
```

### 2. Ask Questions

Use natural language to ask questions about your data:

- "Show me total sales by product category"
- "What are the top 10 customers by revenue?"
- "How many orders were placed last month?"
- "Show me sales trends over the past 6 months"
- "Which products have the highest profit margins?"

### 3. Explore Results

View your results in three ways:
- **Visualization**: Interactive charts and graphs
- **Data Table**: Raw data in a searchable table
- **SQL Details**: See the generated SQL query and explanation

### 4. Explore Schema

Use the Schema Explorer to:
- Browse available tables and columns
- See data types and relationships
- View sample data from each table

## API Endpoints

- `POST /api/connect` - Connect to database
- `POST /api/query` - Process natural language query
- `GET /api/schema` - Get database schema
- `POST /api/sample-data` - Get sample data from table
- `POST /api/disconnect` - Disconnect from database
- `GET /api/health` - Health check

## Security Features

- **Read-only queries**: Only SELECT and WITH statements allowed
- **SQL injection protection**: Query validation and sanitization
- **Query timeouts**: Prevent long-running queries
- **Row limits**: Configurable limits on result sets
- **No credential storage**: Session-based connections only

## Configuration

Environment variables in `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
MAX_QUERY_ROWS=10000
DEFAULT_DB_TIMEOUT=30
```

## Example Queries

The system can handle various types of questions:

### Aggregation Queries
- "What's the total revenue for each product category?"
- "Show me average order value by month"

### Time-based Analysis
- "How did sales perform in Q4 2024?"
- "Show me daily active users for the past month"

### Comparative Analysis
- "Which regions have the highest customer satisfaction?"
- "Compare this year's sales to last year"

### Filtering and Grouping
- "Show me all customers from California with orders over $1000"
- "What are the most popular products in each category?"

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check your connection string format
   - Ensure PostgreSQL is running
   - Verify credentials and database exists

2. **OpenAI API Errors**
   - Verify your API key is correct
   - Check your OpenAI account has sufficient credits
   - Ensure you have access to GPT-4

3. **Query Generation Issues**
   - Make sure your question is clear and specific
   - Check that referenced tables/columns exist in your schema
   - Try rephrasing your question

### Debug Mode

Enable debug logging by setting the log level in `backend/main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Project Structure

```
talk_to_data_ai/
├── backend/
│   ├── agents/          # OpenAI agent and orchestration
│   ├── database/        # Schema inspection and query execution
│   ├── visualization/   # Chart generation with Plotly
│   ├── config.py        # Configuration settings
│   └── main.py          # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── App.jsx      # Main application
│   │   └── main.jsx     # Entry point
│   └── package.json
├── requirements.txt     # Python dependencies
└── README.md
```

### Adding New Features

1. **New Chart Types**: Extend `ChartGenerator` class
2. **Additional Databases**: Modify `SchemaInspector` for new database types
3. **Custom Visualizations**: Add new components to the frontend
4. **Enhanced AI**: Extend function definitions in `QueryAgent`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review the API documentation at http://localhost:8000/docs
3. Open an issue on GitHub

## Roadmap

- [ ] Support for additional databases (MySQL, SQLite, etc.)
- [ ] Advanced visualization types (heatmaps, treemaps, etc.)
- [ ] Query optimization suggestions
- [ ] Export functionality (PDF, CSV, etc.)
- [ ] User authentication and multi-tenant support
- [ ] Query history and favorites
- [ ] Custom dashboard creation
