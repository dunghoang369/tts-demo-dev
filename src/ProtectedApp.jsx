import { useAuth } from './context/AuthContext';
import Login from './components/Login';
import App from './App';

function ProtectedApp() {
  const { authenticated, loading, login } = useAuth();

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        fontSize: '20px',
        fontWeight: '600'
      }}>
        Loading...
      </div>
    );
  }

  if (!authenticated) {
    return <Login onLogin={login} />;
  }

  return <App />;
}

export default ProtectedApp;



