import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Plus, Calendar, Clock, Search, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

export function Gallery() {
  const { user } = useAuth();
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async (searchQuery = '') => {
    setLoading(true);
    try {
      const url = searchQuery ? `/images/?search=${searchQuery}` : '/images/';
      const response = await api.get(url);
      setImages(response.data);
    } catch (err) {
      setError('Failed to load images.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchImages(search);
  };

  const handleDelete = async (imageId) => {
    if (!window.confirm('Delete this image?')) return;
    try {
        await api.delete(`/admin/images/${imageId}`);
        setImages(images.filter(img => img.id !== imageId));
    } catch (err) {
        alert('Failed to delete image. You might not have permission.');
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

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="sm:flex sm:items-center justify-between mb-8">
        <div className="sm:flex-auto">
          <h1 className="text-3xl font-bold leading-tight tracking-tight text-slate-900">Community Gallery</h1>
          <p className="mt-2 text-sm text-slate-700">
            A visual timeline of moments shared by the community.
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <Link to="/upload">
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              New Entry
            </Button>
          </Link>
        </div>
      </div>

      <div className="mb-8 max-w-md">
        <form onSubmit={handleSearch} className="flex gap-2">
            <Input 
                placeholder="Search images..." 
                value={search} 
                onChange={(e) => setSearch(e.target.value)}
            />
            <Button type="submit" variant="secondary">
                <Search className="h-4 w-4" />
            </Button>
        </form>
      </div>

      {loading && (
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-600"></div>
        </div>
      )}

      {error && (
        <div className="mt-6 rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {!loading && images.length === 0 && !error ? (
        <div className="text-center mt-20">
          <h3 className="mt-2 text-sm font-semibold text-slate-900">No entries found</h3>
          <p className="mt-1 text-sm text-slate-500">Try adjusting your search or upload a new image.</p>
        </div>
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {images.map((image) => (
            <div key={image.id} className="flex flex-col overflow-hidden rounded-lg shadow-lg bg-white transition-transform hover:-translate-y-1 hover:shadow-xl relative group">
              <div className="flex-shrink-0 relative">
                <img 
                    className="h-64 w-full object-cover" 
                    src={`http://localhost:5000/images/file/${image.filename}`} 
                    alt={image.description || "Uploaded image"} 
                />
                {user?.is_admin && (
                    <button 
                        onClick={() => handleDelete(image.id)}
                        className="absolute top-2 right-2 bg-red-600 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Delete Image (Admin)"
                    >
                        <Trash2 className="h-4 w-4" />
                    </button>
                )}
              </div>
              <div className="flex flex-1 flex-col justify-between p-6">
                <div className="flex-1">
                  <div className="flex items-center text-sm text-slate-500 mb-3">
                    <Calendar className="mr-1.5 h-4 w-4 flex-shrink-0 text-slate-400" />
                    <p>
                      {formatDate(image.uploaded_at)}
                    </p>
                  </div>
                  <p className="text-xl font-semibold text-slate-900">{image.description}</p>
                  <p className="mt-2 text-sm text-slate-500">by {image.author_email}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
