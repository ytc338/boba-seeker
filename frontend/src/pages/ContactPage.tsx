import { useState } from 'react';
import { submitFeedback } from '../services/api';
import './ContactPage.css';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    type: 'suggestion', // default
    message: ''
  });
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.message.trim()) {
      return;
    }

    try {
      setStatus('submitting');
      await submitFeedback(formData);
      setStatus('success');
      setFormData({ name: '', email: '', type: 'suggestion', message: '' });
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      setStatus('error');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="contact-page">
      <div className="contact-header">
        <h1>Contact & Suggestions</h1>
        <p className="text-muted">Have a feature request, found a bug, or just want to verify a shop? Let us know!</p>
      </div>

      <div className="contact-form">
        {status === 'success' && (
          <div className="alert alert-success">
            Thanks for your message! We'll look into it.
          </div>
        )}
        
        {status === 'error' && (
          <div className="alert alert-error">
            Something went wrong. Please try again later.
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="type">Topic</label>
            <select
              id="type"
              name="type"
              className="form-control"
              value={formData.type}
              onChange={handleChange}
            >
              <option value="suggestion">Suggestion</option>
              <option value="contact">General Contact</option>
              <option value="bug">Report a Bug</option>
              <option value="data">Data Correction</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="name">Name (Optional)</label>
            <input
              type="text"
              id="name"
              name="name"
              className="form-control"
              value={formData.name}
              onChange={handleChange}
              placeholder="Your name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email (Optional)</label>
            <input
              type="email"
              id="email"
              name="email"
              className="form-control"
              value={formData.email}
              onChange={handleChange}
              placeholder="Your email (if you want a reply)"
            />
          </div>

          <div className="form-group">
            <label htmlFor="message">Message</label>
            <textarea
              id="message"
              name="message"
              className="form-control"
              value={formData.message}
              onChange={handleChange}
              placeholder="What's on your mind?"
              required
              rows={5}
            />
          </div>

          <button 
            type="submit" 
            className="btn-submit" 
            disabled={status === 'submitting'}
          >
            {status === 'submitting' ? 'Sending...' : 'Send Message'}
          </button>
        </form>
      </div>
    </div>
  );
}
