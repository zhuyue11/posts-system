import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

function AuthCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const token = searchParams.get('token');
    const userId = searchParams.get('user_id');
    const name = searchParams.get('name');
    const email = searchParams.get('email');
    const picture = searchParams.get('picture');

    if (token && userId && name && email) {
      // Store user info in localStorage
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify({
        userId,
        name,
        email,
        picture
      }));

      // Redirect to main page
      navigate('/');
    } else {
      // If authentication failed, redirect to login
      navigate('/login');
    }
  }, [searchParams, navigate]);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh'
    }}>
      <div>Loading...</div>
    </div>
  );
}

export default AuthCallback;
