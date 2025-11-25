import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Main.css';

function Main() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [newPost, setNewPost] = useState({ subject: '', content: '' });
  const [loading, setLoading] = useState(false);
  const [expandedPostId, setExpandedPostId] = useState(null);
  const [comments, setComments] = useState({});
  const [newComment, setNewComment] = useState({});
  const [commentLoading, setCommentLoading] = useState({});
  const [editingPostId, setEditingPostId] = useState(null);
  const [editingCommentId, setEditingCommentId] = useState(null);
  const [editPostData, setEditPostData] = useState({ subject: '', content: '' });
  const [editCommentContent, setEditCommentContent] = useState('');

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
      const url = new URL('http://localhost:8000/api/posts');
      url.searchParams.append('google_user_id', user.userId);
      url.searchParams.append('author_name', user.name);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subject: newPost.subject,
          content: newPost.content,
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

  const toggleComments = async (postId) => {
    if (expandedPostId === postId) {
      setExpandedPostId(null);
    } else {
      setExpandedPostId(postId);
      if (!comments[postId]) {
        await fetchComments(postId);
      }
    }
  };

  const fetchComments = async (postId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/posts/${postId}/comments`);
      if (response.ok) {
        const data = await response.json();
        setComments(prev => ({ ...prev, [postId]: data }));
      }
    } catch (error) {
      console.error('Error fetching comments:', error);
    }
  };

  const handleAddComment = async (postId) => {
    const commentText = newComment[postId]?.trim();
    if (!commentText) return;

    setCommentLoading(prev => ({ ...prev, [postId]: true }));
    try {
      const url = new URL(`http://localhost:8000/api/posts/${postId}/comments`);
      url.searchParams.append('google_user_id', user.userId);
      url.searchParams.append('author_name', user.name);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: commentText,
        }),
      });

      if (response.ok) {
        setNewComment(prev => ({ ...prev, [postId]: '' }));
        await fetchComments(postId);
        // Update post comment count
        setPosts(posts.map(p =>
          p.id === postId
            ? { ...p, comment_count: (p.comment_count || 0) + 1 }
            : p
        ));
      }
    } catch (error) {
      console.error('Error adding comment:', error);
    } finally {
      setCommentLoading(prev => ({ ...prev, [postId]: false }));
    }
  };

  const handleDeletePost = async (postId) => {
    if (!window.confirm('Are you sure you want to delete this post? This will also delete all comments.')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/posts/${postId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setPosts(posts.filter(p => p.id !== postId));
        if (expandedPostId === postId) {
          setExpandedPostId(null);
        }
      }
    } catch (error) {
      console.error('Error deleting post:', error);
    }
  };

  const handleDeleteComment = async (postId, commentId) => {
    if (!window.confirm('Are you sure you want to delete this comment?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/comments/${commentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        await fetchComments(postId);
        // Update post comment count
        setPosts(posts.map(p =>
          p.id === postId
            ? { ...p, comment_count: Math.max((p.comment_count || 0) - 1, 0) }
            : p
        ));
      }
    } catch (error) {
      console.error('Error deleting comment:', error);
    }
  };

  const startEditPost = (post) => {
    setEditingPostId(post.id);
    setEditPostData({ subject: post.subject, content: post.content });
  };

  const cancelEditPost = () => {
    setEditingPostId(null);
    setEditPostData({ subject: '', content: '' });
  };

  const handleUpdatePost = async (postId) => {
    if (!editPostData.subject.trim() || !editPostData.content.trim()) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/posts/${postId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          subject: editPostData.subject,
          content: editPostData.content,
        }),
      });

      if (response.ok) {
        const updatedPost = await response.json();
        setPosts(posts.map(p => p.id === postId ? updatedPost : p));
        setEditingPostId(null);
        setEditPostData({ subject: '', content: '' });
      }
    } catch (error) {
      console.error('Error updating post:', error);
    }
  };

  const startEditComment = (comment) => {
    setEditingCommentId(comment.id);
    setEditCommentContent(comment.content);
  };

  const cancelEditComment = () => {
    setEditingCommentId(null);
    setEditCommentContent('');
  };

  const handleUpdateComment = async (postId, commentId) => {
    if (!editCommentContent.trim()) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/comments/${commentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          content: editCommentContent,
        }),
      });

      if (response.ok) {
        await fetchComments(postId);
        setEditingCommentId(null);
        setEditCommentContent('');
      }
    } catch (error) {
      console.error('Error updating comment:', error);
    }
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
                    <div className="post-author-info">
                      <strong>{post.author_name}</strong>
                      <span className="post-date">
                        {new Date(post.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {post.google_user_id === user.userId && (
                      <div className="post-actions">
                        {editingPostId === post.id ? (
                          <>
                            <button
                              className="save-button"
                              onClick={() => handleUpdatePost(post.id)}
                              title="Save changes"
                            >
                              Save
                            </button>
                            <button
                              className="cancel-button"
                              onClick={cancelEditPost}
                              title="Cancel editing"
                            >
                              Cancel
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              className="edit-button"
                              onClick={() => startEditPost(post)}
                              title="Edit post"
                            >
                              Edit
                            </button>
                            <button
                              className="delete-button"
                              onClick={() => handleDeletePost(post.id)}
                              title="Delete post"
                            >
                              Delete
                            </button>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                  {editingPostId === post.id ? (
                    <div className="edit-post-form">
                      <input
                        type="text"
                        value={editPostData.subject}
                        onChange={(e) => setEditPostData({ ...editPostData, subject: e.target.value })}
                        className="edit-input"
                        maxLength="255"
                      />
                      <textarea
                        value={editPostData.content}
                        onChange={(e) => setEditPostData({ ...editPostData, content: e.target.value })}
                        className="edit-textarea"
                        maxLength="280"
                      />
                      <span className="char-count">{editPostData.content.length}/280</span>
                    </div>
                  ) : (
                    <>
                      <h3 className="post-subject">{post.subject}</h3>
                      <p className="post-content">{post.content}</p>
                    </>
                  )}
                  <div className="post-footer">
                    <button
                      className="comments-toggle"
                      onClick={() => toggleComments(post.id)}
                    >
                      {expandedPostId === post.id ? '▼' : '▶'} {post.comment_count || 0} comments
                    </button>
                  </div>

                  {expandedPostId === post.id && (
                    <div className="comments-section">
                      <div className="comments-list">
                        {comments[post.id]?.length > 0 ? (
                          comments[post.id].map((comment) => (
                            <div key={comment.id} className="comment">
                              <div className="comment-header">
                                <div className="comment-author-info">
                                  <strong>{comment.author_name}</strong>
                                  <span className="comment-date">
                                    {new Date(comment.created_at).toLocaleDateString()}
                                  </span>
                                </div>
                                {comment.google_user_id === user.userId && (
                                  <div className="comment-actions">
                                    {editingCommentId === comment.id ? (
                                      <>
                                        <button
                                          className="save-comment-button"
                                          onClick={() => handleUpdateComment(post.id, comment.id)}
                                          title="Save changes"
                                        >
                                          Save
                                        </button>
                                        <button
                                          className="cancel-comment-button"
                                          onClick={cancelEditComment}
                                          title="Cancel editing"
                                        >
                                          Cancel
                                        </button>
                                      </>
                                    ) : (
                                      <>
                                        <button
                                          className="edit-comment-button"
                                          onClick={() => startEditComment(comment)}
                                          title="Edit comment"
                                        >
                                          Edit
                                        </button>
                                        <button
                                          className="delete-comment-button"
                                          onClick={() => handleDeleteComment(post.id, comment.id)}
                                          title="Delete comment"
                                        >
                                          Delete
                                        </button>
                                      </>
                                    )}
                                  </div>
                                )}
                              </div>
                              {editingCommentId === comment.id ? (
                                <div className="edit-comment-form">
                                  <textarea
                                    value={editCommentContent}
                                    onChange={(e) => setEditCommentContent(e.target.value)}
                                    className="edit-comment-textarea"
                                    maxLength="280"
                                  />
                                  <span className="char-count">{editCommentContent.length}/280</span>
                                </div>
                              ) : (
                                <p className="comment-content">{comment.content}</p>
                              )}
                            </div>
                          ))
                        ) : (
                          <p className="no-comments">No comments yet. Be the first to comment!</p>
                        )}
                      </div>

                      <div className="add-comment">
                        <textarea
                          placeholder="Write a comment..."
                          value={newComment[post.id] || ''}
                          onChange={(e) =>
                            setNewComment({ ...newComment, [post.id]: e.target.value })
                          }
                          className="comment-textarea"
                          maxLength="280"
                        />
                        <div className="comment-form-footer">
                          <span className="char-count">
                            {(newComment[post.id] || '').length}/280
                          </span>
                          <button
                            onClick={() => handleAddComment(post.id)}
                            disabled={!newComment[post.id]?.trim() || commentLoading[post.id]}
                            className="comment-button"
                          >
                            {commentLoading[post.id] ? 'Adding...' : 'Add Comment'}
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
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
