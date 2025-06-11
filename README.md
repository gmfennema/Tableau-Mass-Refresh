# Tableau Mass Refresh - Vercel Deployment

A modern web application for bulk refreshing Tableau extracts with advanced filtering and management features.

## Features

- **Modern UI/UX**: Clean, responsive interface built with Tailwind CSS
- **Bulk Operations**: Select and refresh multiple workbooks at once
- **Advanced Filtering**: Search by name, project, owner with real-time filtering
- **Visual Progress**: Real-time progress tracking for refresh operations
- **Export Functionality**: Export workbook lists to CSV
- **Activity Log**: Detailed logging of all operations

## Deployment on Vercel

### Prerequisites

1. A Vercel account (free tier available)
2. Git repository containing this code
3. Tableau Server with Personal Access Token capability

### Deploy to Vercel

#### Option 1: Deploy with Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Clone and navigate to your repository:
```bash
git clone <your-repo-url>
cd tableau-mass-refresh
```

3. Deploy to Vercel:
```bash
vercel
```

4. Follow the prompts and your app will be deployed!

#### Option 2: Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your Git repository
4. Vercel will automatically detect the Python configuration
5. Click "Deploy"

### Configuration Files

The repository includes these Vercel-specific files:

- **`vercel.json`**: Vercel configuration for Python serverless functions
- **`requirements.txt`**: Python dependencies
- **`api/index.py`**: Main Flask application adapted for serverless

### Environment Variables

No environment variables are required - authentication is handled through the web interface using Tableau Personal Access Tokens.

## Tableau Personal Access Token Setup

To use this application, you need to create a Personal Access Token in Tableau Server:

1. Sign in to Tableau Server
2. Go to your user menu → My Account Settings
3. Navigate to Personal Access Tokens
4. Click "Create new token"
5. Enter a token name and click "Create"
6. Copy the token name and secret for use in this application

## Local Development

To run the application locally:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask application:
```bash
python api/index.py
```

3. Open your browser to `http://localhost:5000`

## API Endpoints

- `GET /` - Main application interface
- `POST /api/signin` - Authenticate with Tableau Server
- `POST /api/workbooks` - Fetch workbooks from Tableau Server
- `POST /api/refresh` - Start extract refresh jobs
- `GET /api/jobs/<job_id>` - Check refresh job status
- `GET /health` - Health check endpoint

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Tailwind CSS
- **Icons**: Feather Icons
- **Deployment**: Vercel Serverless Functions

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Security Notes

- Personal Access Tokens are not stored server-side
- All communication with Tableau Server uses HTTPS
- Authentication tokens are kept in browser memory only
- No persistent storage of credentials

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Verify your server URL, site content URL, and PAT credentials
2. **Workbooks Not Loading**: Check network connectivity and Tableau Server permissions
3. **Refresh Failed**: Ensure you have extract refresh permissions on the selected workbooks

### Support

For issues related to:
- **Tableau Server**: Contact your Tableau administrator
- **Application Bugs**: Create an issue in the repository
- **Vercel Deployment**: Check [Vercel documentation](https://vercel.com/docs)

## License

This project is open source and available under the MIT License.
