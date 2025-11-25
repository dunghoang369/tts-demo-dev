# TTS Demo - React Frontend with Authentication

A React-based Text-to-Speech demo application with a modern dark UI, similar to ElevenLabs Studio. Now with FastAPI backend and JWT authentication!

## Features

- **Dual Authentication System**: Login with username OR email (@namisense.ai domain)
- **JWT Token Authentication**: Secure, stateless authentication with JSON Web Tokens
- **FastAPI Backend**: Modern async Python backend with automatic API documentation
- **Session Management**: Token-based authentication with logout functionality
- **Modern ElevenLabs-style Interface**: Polished UI with gradient accents and smooth animations
- **Tabbed Settings Panel**: Switch between Settings and History tabs
- **Voice Selection**: Visual voice cards with gradient avatars and easy selection
- **Model Selection**: Detailed model cards with version badges and descriptions
- **Advanced Parameter Controls**:
  - **Speed**: Adjust speech speed from 0.25x to 4.0x
  - **Stability**: Control voice stability from 0 to 1
  - **Similarity**: Fine-tune similarity boost from 0 to 1
  - **Style Exaggeration**: Adjust style from 0 to 1
- **Quick Start Examples**: 6 pre-written prompts to get started quickly
  - Narrate a story
  - Tell a silly joke
  - Record an advertisement
  - Speak in different languages
  - Direct a dramatic movie scene
  - Guide a meditation class
- **Playback Controls**: Speak, Pause, Resume, Stop, Clear
- **Responsive Design**: Works on mobile and desktop
- **Dark Theme**: Modern dark UI with gradient backgrounds
- **Mock API Integration**: Ready for backend connection with full parameter support

## Getting Started

### Quick Start (Both Servers)

The easiest way to run both the backend and frontend:

```bash
./start-servers.sh
```

This will start both servers automatically. Access the app at `http://localhost:5173`

### Manual Setup

#### 1. Backend Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or venv\Scripts\activate on Windows

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Run the backend server
python server.py
```

Backend will run on `http://localhost:5000`

#### 2. Frontend Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on `http://localhost:5173`

### Demo Credentials

Use these credentials to login:

**Username/Password:**
- **Username:** admin | **Password:** admin123
- **Username:** demo  | **Password:** demo123
- **Username:** user  | **Password:** password

**Email/Password (@namisense.ai only):**
- **Email:** admin@namisense.ai | **Password:** admin123
- **Email:** user@namisense.ai  | **Password:** password123
- **Email:** demo@namisense.ai  | **Password:** demo123

### Build for Production

```bash
npm run build
```

## Project Structure

```
src/
├── api/
│   ├── ttsService.js       # Vietnamese TTS API service
│   └── authService.js      # Authentication API service
├── components/
│   ├── TextEditor.jsx      # Text input and playback controls
│   ├── TextEditor.css
│   ├── SettingsPanel.jsx   # Voice and model settings
│   ├── SettingsPanel.css
│   ├── Login.jsx           # Login page component
│   └── Login.css
├── context/
│   └── AuthContext.jsx     # Authentication state management
├── App.jsx                 # Main application layout
├── App.css                 # App-level styles
├── ProtectedApp.jsx        # Protected route wrapper
├── index.css               # Global styles
└── main.jsx                # React entry point

backend/
├── server.py               # Flask authentication server
├── requirements.txt        # Python dependencies
└── README.md              # Backend documentation
```

## Authentication Flow

1. User lands on the app
2. If not authenticated, the login page is displayed
3. User enters username OR email (@namisense.ai) + password
4. Backend validates credentials:
   - If email: validates @namisense.ai domain
   - If username: validates against username database
5. Backend creates a session on success
6. Frontend redirects to the main TTS application
7. User can logout via the logout button in the header
8. Session is cleared on logout (not persistent on page refresh)

## Vietnamese TTS API Integration

The app is integrated with a Vietnamese TTS backend:

**API Endpoint**: `https://aft.namisense.ai/tts/offline`

**Available Voices**:
- 01_hannah - Hannah
- 02_thuthuy - Thu Thúy
- 03_kimchi - Kim Chi
- 04_hongphuong - Hồng Phượng
- 05_phuonganh - Phương Anh
- 06_sonlong - Sơn Long

**Sample Rates** (Models):
- 16kHz (Standard)
- 22kHz (High Quality)
- 44kHz (Premium)

The API implementation in `src/api/ttsService.js`:

```javascript
export async function synthesize(text, voice, model) {
  const params = new URLSearchParams({
    text: text,
    accent: voice || '01_hannah',
    sample_rate: model || '16000',
    audio_format: 'wav'
  });
  
  const response = await fetch(`https://aft.namisense.ai/tts/offline?${params}`);
  const blob = await response.blob();
  const audioUrl = URL.createObjectURL(blob);
  
  return { audioUrl, blob };
}
```

Try it with Vietnamese text like:
- "Xin chào, tôi là trợ lý ảo"
- "Hôm nay tôi đi học"

## Technologies

- React 18
- Vite
- CSS Variables for theming
- Vietnamese TTS API (aft.namisense.ai)

## License

MIT
