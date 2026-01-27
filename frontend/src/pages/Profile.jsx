import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/Button';
import { Plus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

export function Profile() {
  const { user } = useAuth();
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async () => {
    try {
      const response = await api.get('/images/?user_id=me');
      setImages(response.data);
    } catch (err) {
      setError('Failed to load images.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    }).format(date);
  };

  if (loading) return <div className="p-10 text-center">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
            <h1 className="text-3xl font-bold text-slate-900">My Profile</h1>
            <p className="mt-1 text-slate-600">{user?.email}</p>
        </div>
        <Link to="/upload">
            <Button className="gap-2">
                <Plus className="h-4 w-4" />
                New Entry
            </Button>
        </Link>
      </div>

      {error && <p className="text-red-500 mb-4">{error}</p>}

      <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
        {images.map((image) => (
          <div key={image.id} className="flex flex-col overflow-hidden rounded-lg shadow-lg bg-white">
            <div className="flex-shrink-0 relative">
              <img 
                  className="h-48 w-full object-cover" 
                  src={`http://localhost:5000/images/file/${image.filename}`} 
                  alt={image.description} 
              />
            </div>
            <div className="flex flex-1 flex-col justify-between p-6">
              <div className="flex-1">
                <p className="text-sm font-medium text-brand-600 mb-2">
                  {formatDate(image.uploaded_at)}
                </p>
                <p className="text-base text-slate-900">{image.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {images.length === 0 && (
          <div className="text-center py-20 bg-slate-50 rounded-lg border-2 border-dashed border-slate-200">
              <p className="text-slate-500">No entries yet.</p>
          </div>
      )}
    </div>
  );
}
