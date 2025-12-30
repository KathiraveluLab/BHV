#!/bin/bash
# BHV GitHub Setup Script

echo "🚀 Setting up BHV for GitHub..."

# Navigate to project directory
cd "$(dirname "$0")"

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git initialized"
fi

# Create and switch to new branch
git checkout -b feat/bhv-complete-implementation
echo "✅ Created branch: feat/bhv-complete-implementation"

# Add all files
git add .
echo "✅ Added all files"

# Commit with descriptive message
git commit -m "feat: complete BHV application foundation

- Complete Flask web application with authentication
- Secure image upload and storage system
- Role-based access control (Patient/Social Worker/Admin)
- Healthcare-compliant audit trails and security
- System diagnostics and health monitoring
- Single-command deployment with auto-setup
- Responsive UI with Bootstrap design
- Comprehensive testing and documentation

Ready for production deployment in healthcare networks."

echo "✅ Committed changes"

# Instructions for GitHub setup
echo ""
echo "🔗 Next steps for GitHub:"
echo "1. Create repository at: https://github.com/new"
echo "2. Run: git remote add origin https://github.com/YOUR_USERNAME/BHV.git"
echo "3. Run: git push -u origin feat/bhv-complete-implementation"
echo "4. Create pull request on GitHub"
echo ""
echo "📋 Or copy this command:"
echo "git remote add origin https://github.com/YOUR_USERNAME/BHV.git && git push -u origin feat/bhv-complete-implementation"