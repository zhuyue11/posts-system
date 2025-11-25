import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Main.css';

function Main() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [newPost, setNewPost] = useState({ subject: '', content: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (!token || !userData) {
      navigate('/login');
      return;
    }

    setUser(JSON.parse(userData));
    fetchPosts();
  }, [navigate]);

  const fetchPosts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/posts');
      if (response.ok) {
        const data = await response.json();
        setPosts(data);
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
    }
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();
    if (!newPost.subject.trim() || !newPost.content.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subject: newPost.subject,
          content: newPost.content,
          google_user_id: user.userId,
          author_name: user.name,
        }),
      });

      if (response.ok) {
        setNewPost({ subject: '', content: '' });
        fetchPosts();
      }
    } catch (error) {
      console.error('Error creating post:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="main-container">
      <header className="header">
        <h1>Posts System</h1>
        <div className="user-info">
          {user.picture && <img src={user.picture} alt={user.name} className="avatar" />}
          <span>{user.name}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </header>

      <div className="content">
        <div className="create-post-section">
          <h2>Create New Post</h2>
          <form onSubmit={handleCreatePost} className="post-form">
            <input
              type="text"
              placeholder="Subject"
              value={newPost.subject}
              onChange={(e) => setNewPost({ ...newPost, subject: e.target.value })}
              className="post-input"
              maxLength="255"
              required
            />
            <textarea
              placeholder="What's on your mind?"
              value={newPost.content}
              onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
              className="post-textarea"
              maxLength="280"
              required
            />
            <div className="form-footer">
              <span className="char-count">{newPost.content.length}/280</span>
              <button type="submit" disabled={loading} className="submit-button">
                {loading ? 'Posting...' : 'Post'}
              </button>
            </div>
          </form>
        </div>

        <div className="posts-section">
          <h2>Recent Posts</h2>
          <div className="posts-list">
            {posts.length === 0 ? (
              <p className="no-posts">No posts yet. Be the first to post!</p>
            ) : (
              posts.map((post) => (
                <div key={post.id} className="post-card">
                  <div className="post-header">
                    <strong>{post.author_name}</strong>
                    <span className="post-date">
                      {new Date(post.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="post-subject">{post.subject}</h3>
                  <p className="post-content">{post.content}</p>
                  <div className="post-footer">
                    <span className="comments-count">
                      {post.comments?.length || 0} comments
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Main;
