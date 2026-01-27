import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from './Button';
import { LogOut, Upload as UploadIcon, Image as ImageIcon, LayoutDashboard, Shield, User } from 'lucide-react';

export function Navbar() {
  const { isAuthenticated, logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 justify-between items-center">
          <div className="flex items-center">
            <Link to={isAuthenticated ? "/dashboard" : "/"} className="flex items-center gap-2">
              <div className="bg-brand-600 rounded-lg p-1.5">
                <LayoutDashboard className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold text-slate-900 tracking-tight">
                BHV
              </span>
            </Link>
          </div>

          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                {user?.is_admin && (
                  <Link to="/admin">
                    <Button variant="ghost" className="hidden sm:inline-flex gap-2 text-purple-600 hover:bg-purple-50 hover:text-purple-700">
                      <Shield className="h-4 w-4" />
                      Admin
                    </Button>
                  </Link>
                )}
                <Link to="/gallery">
                    <Button variant="ghost" className="hidden sm:inline-flex gap-2">
                        <ImageIcon className="h-4 w-4" />
                        Gallery
                    </Button>
                </Link>
                <Link to="/upload">
                    <Button variant="primary" className="gap-2">
                        <UploadIcon className="h-4 w-4" />
                        <span className="hidden sm:inline">Upload</span>
                    </Button>
                </Link>
                <div className="h-6 w-px bg-slate-200 mx-2 hidden sm:block"></div>
                <div className="flex items-center gap-4">
                    <Link to="/profile" className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900">
                        <User className="h-4 w-4" />
                        <span className="hidden md:block">{user?.email}</span>
                    </Link>
                    <Button 
                        variant="secondary" 
                        onClick={handleLogout}
                        className="p-2 sm:px-4"
                    >
                        <LogOut className="h-4 w-4 sm:mr-2" />
                        <span className="hidden sm:inline">Logout</span>
                    </Button>
                </div>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost">Log in</Button>
                </Link>
                <Link to="/signup">
                  <Button variant="primary">Sign up</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
