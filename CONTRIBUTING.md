# Contributing to BHV (Behavioral Health Vault)

Thank you for your interest in contributing to BHV! We welcome contributions from everyone who wants to help improve healthcare technology for people with serious mental illnesses and social determinants.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)
- Basic understanding of Python and databases.

### Setting Up Your Development Environment

1. **Fork the Repository**
   
   Click the "Fork" button at the top right of the repository page to create your own copy.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/KathiraveluLab/BHV.git
   cd BHV
   ```

3. **Add Upstream Remote**

   ```bash
   git remote add upstream https://github.com/KathiraveluLab/BHV.git
   git remote -v  # Verify the new remote named 'upstream'
   ```

4. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

6. **Set Up Pre-commit Hooks** (if configured)

   ```bash
   pre-commit install
   ```

7. **Run the Application**

   Follow the instructions in the README.md to run the application locally and verify your setup.

## How to Contribute

### Types of Contributions

We welcome many types of contributions:

- **Bug Reports**: Help us identify issues
- **Feature Requests**: Suggest new functionality
- **Documentation**: Improve or add documentation
- **Bug Fixes**: Submit fixes for identified issues
- **Performance Improvements**: Optimize existing code
- **UI/UX Improvements**: Enhance user experience
- **Tests**: Add or improve test coverage
- **Accessibility**: Improve accessibility features
- **Security**: Report or fix security vulnerabilities

## Development Workflow

1. **Sync Your Fork**

   ```bash
   git checkout dev
   git fetch upstream
   git merge upstream/dev
   ```

2. **Create a Feature Branch**

   Use descriptive branch names:
   ```bash
   git checkout -b feature/add-image-compression
   git checkout -b fix/login-validation-error
   git checkout -b docs/update-installation-guide
   git checkout -b refactor/optimize-database-queries
   ```

3. **Make Your Changes**

   - Write clean, readable code
   - Follow the project's code style
   - Add tests for new features
   - Update documentation as needed
   

4. **Test Your Changes**


5. **Commit Your Changes**

   See [Commit Message Guidelines](#commit-message-guidelines)

6. **Push to Your Fork**

   ```bash
   git push origin feature/your-feature-name
   ```

7. **Submit a Pull Request to `dev` Branch**

   See [Pull Request Guidelines](#pull-request-guidelines)

## Issue Guidelines

### Before Creating an Issue

1. **Search Existing Issues**: Check if the issue already exists
2. **Check Documentation**: Ensure it's not covered in docs
3. **Verify the Bug**: Make sure it's reproducible

### Creating a Meaningful Issue

#### Bug Report Template

**Title Format**: `[BUG] Brief description of the issue`

**Example**: `[BUG] Image upload fails for files larger than 5MB`

**Content**:
```markdown
## Description
A clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Upload image '...'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.


## Screenshots
If applicable, add screenshots.

## Additional Context
Any other relevant information.

```

#### Feature Request Template

**Title Format**: `[FEATURE] Brief description of the feature`

**Example**: `[FEATURE] Add bulk image upload capability`

**Content**:
```markdown
## Problem Statement
Describe the problem this feature would solve.

## Proposed Solution
Describe your proposed solution.

## Alternatives Considered
What other approaches did you consider?

## Use Case
Who would benefit from this feature and how?

## Additional Context
Any other relevant information, mockups, or examples.

#### Documentation Issue Template

**Title Format**: `[DOCS] Brief description of documentation issue`

**Example**: `[DOCS] Missing installation instructions for PostgreSQL`

#### Other Issue Types

- `[QUESTION]` - For questions about the project
- `[SECURITY]` - For security-related issues (see Security Policy)
- `[PERFORMANCE]` - For performance-related issues
- `[ACCESSIBILITY]` - For accessibility improvements
- `[REFACTOR]` - For code refactoring suggestions

### Issue Labels

Issues will be labeled by maintainers:
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `priority: high` - High priority
- `security` - Security-related
- `wontfix` - This will not be worked on

```

## Pull Request Guidelines


### PR Title Format

Use conventional commit format:

```
<type>(<scope>): <subject>
```

**Types**:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `security`: Security fixes

**Examples**:
- `feat(upload): add support for bulk image uploads`
- `fix(auth): resolve login validation error for special characters`
- `docs(readme): update installation instructions`
- `refactor(database): optimize patient record queries`
- `security(api): fix SQL injection vulnerability in search`

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Related Issue
Fixes #(issue number)
Closes #(issue number)
Related to #(issue number)

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Security fix

## Changes Made
- Change 1
- Change 2
- Change 3


## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Additional Notes
Any additional information for reviewers.
```

### PR Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Code Review**: At least one maintainer review required
3. **Revisions**: Address requested changes promptly
4. **Approval**: Once approved, a maintainer will merge
5. **Cleanup**: Delete your branch after merge

### PR Best Practices

- Keep PRs focused and small (easier to review)
- One feature/fix per PR
- Link related issues
- Respond to feedback constructively
- Keep your PR up to date with the main branch
- Be patient - reviews take time

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Example

```
feat(upload): add image compression before storage

Implement automatic image compression using Pillow to reduce
storage requirements. Images are compressed to 85% quality
while maintaining visual fidelity.

Closes #123
```

### Rules

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- First line should be 50 characters or less
- Include body if changes need explanation
- Reference issues and PRs in footer

## Code Style Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 88 characters (Black formatter default)
- Use meaningful variable and function names
- Add docstrings to functions and classes


### Frontend Style

- Use minimal styles and components.
- We don't need any modern or fancy design.

### Database

- Use MongoDB for Database.
- Using Github Repo as a Database(Idea)


## Documentation

### What to Document

- New features and how to use them
- API endpoints and parameters
- Configuration options
- Installation and setup procedures
- Troubleshooting common issues

### Documentation Style

- Be clear and concise
- Use examples where helpful
- Keep it up to date
- Use proper grammar and spelling
- Structure with headers and lists


## Community

### Getting Help

- **Issues**: Create an issue for bugs or questions.
- **Discussions**: Use GitHub Discussions for general questions and ideas.
- **Email**: Contact maintainers for any issues/help needed.

### Introducing Yourself in Discussions

We encourage new contributors to introduce themselves! Go to the **Discussions** tab and:

1. Click on the "Introductions" category
2. Start a new discussion
3. Tell us about yourself:
   - Your name/username
   - Your background (developer, healthcare professional, student, etc.)
   - What interests you about BHV
   - What you'd like to contribute
   - Any questions you have

**Example Introduction**:

```markdown
Hi everyone! 👋

I'm [Your Name], a [your role] with experience in [relevant skills]. 

I'm interested in BHV because [reason - e.g., "I work in healthcare and want to 
improve mental health record systems"].

I'm hoping to contribute by [what you want to do - e.g., "improving the UI/UX" 
or "adding test coverage"].

Looking forward to working with you all!
```

### Communication Guidelines

- Be respectful and inclusive
- Assume good intentions
- Provide constructive feedback
- Help others learn and grow
- Acknowledge contributions

### Recognition

We value all contributions! Contributors will be:
- Listed in our CONTRIBUTORS.md file
- Mentioned in release notes
- Acknowledged in the project

## Security

### Reporting Security Vulnerabilities

**DO NOT** create public issues for security vulnerabilities.

Please report security issues privately:
1. Create a security advisory on GitHub
2. Or email the maintainers directly

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## License

By contributing to BHV, you agree that your contributions will be licensed under the same license as the project (see [LICENSE](LICENSE)).

---

## Questions?

If you have questions about contributing, feel free to:
- Open a discussion on GitHub
- Check existing issues and discussions
- Reach out to maintainers

Thank you for contributing to BHV and helping improve mental health care technology!

---

**Happy Contributing!** 🎉