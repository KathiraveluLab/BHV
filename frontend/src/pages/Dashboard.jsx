import { Link } from 'react-router-dom';
import { Upload, Image as ImageIcon, Plus, ArrowRight } from 'lucide-react';
import { Button } from '../components/Button';
import { useAuth } from '../context/AuthContext';

export function Dashboard() {
  const { user } = useAuth();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <header className="mb-10">
        <h1 className="text-3xl font-bold leading-tight tracking-tight text-slate-900">
          Welcome back, {user?.email}
        </h1>
        <p className="mt-2 text-lg text-slate-600">
          Your personal space for reflection and growth.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="relative flex flex-col overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-900/5 transition-all hover:shadow-md">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-50">
            <Upload className="h-6 w-6 text-brand-600" />
          </div>
          <h3 className="mt-4 text-lg font-medium text-slate-900">Upload Entry</h3>
          <p className="mt-2 text-slate-600 flex-1">
            Capture a moment or thought. Upload an image and add a narrative to track your journey.
          </p>
          <div className="mt-6">
            <Link to="/upload">
              <Button variant="outline" className="w-full justify-between">
                Upload New
                <Plus className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>

        <div className="relative flex flex-col overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-900/5 transition-all hover:shadow-md">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent-50">
            <ImageIcon className="h-6 w-6 text-accent-600" />
          </div>
          <h3 className="mt-4 text-lg font-medium text-slate-900">View Gallery</h3>
          <p className="mt-2 text-slate-600 flex-1">
            Browse through your past entries. Reflect on your progress and memories.
          </p>
          <div className="mt-6">
            <Link to="/gallery">
              <Button variant="outline" className="w-full justify-between">
                View All
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
