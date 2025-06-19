# Contributing to R3nameX

First off, thank you for considering contributing to R3nameX! 🎉 

This document provides guidelines and instructions for contributing to the project. Following these guidelines helps maintain code quality and makes the review process smoother for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Code Contributions](#code-contributions)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code:

- **Be Respectful**: Treat everyone with respect. No harassment, discrimination, or inappropriate behavior.
- **Be Professional**: Keep discussions focused on the project and constructive.
- **Be Collaborative**: Work together to resolve conflicts and find solutions.
- **Be Inclusive**: Welcome newcomers and help them get started.

## How Can I Contribute?

### Reporting Bugs 🐛

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

**Bug Report Template:**
```markdown
**Description**
A clear and concise description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. Select option '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Windows 10, Ubuntu 20.04, macOS 12]
- Python version: [e.g., 3.8.5]
- R3nameX version: [e.g., 2.0.0]

**Additional Context**
Add any other context, error messages, or screenshots.
```

### Suggesting Features 💡

Feature requests are welcome! Please provide:

**Feature Request Template:**
```markdown
**Feature Description**
Clear description of the feature and its benefits.

**Use Case**
Explain how this feature would be used and who would benefit.

**Proposed Solution**
Your idea for how this could be implemented (optional).

**Alternatives**
Any alternative solutions you've considered.
```

### Code Contributions 🚀

We love code contributions! Here's how to get started:

1. **Find an Issue**: Look for issues labeled `good first issue` or `help wanted`
2. **Comment**: Let us know you're working on it
3. **Fork & Branch**: Create your feature branch
4. **Code**: Make your changes
5. **Test**: Ensure all tests pass
6. **Document**: Update documentation if needed
7. **Submit**: Create a Pull Request

## Development Setup

### Prerequisites
- Python 3.6 or higher
- Git

### Setup Steps

1. **Fork the Repository**
   ```bash
   # Click 'Fork' button on GitHub
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/r3namex.git
   cd r3namex
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/stuxboynet/r3namex.git
   ```

4. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

5. **Make Your Changes**
   ```bash
   # Edit files...
   # Test your changes
   python r3namex.py -h  # Ensure it still works
   ```

## Pull Request Process

### Before Submitting

1. **Update from Upstream**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Test Your Changes**
   - Run the script with various options
   - Test edge cases
   - Ensure backward compatibility

3. **Update Documentation**
   - Update README.md if adding features
   - Update help text in the script
   - Add/update docstrings

4. **Follow Code Style**
   - Use 4 spaces for indentation
   - Follow PEP 8 guidelines
   - Keep lines under 100 characters

### PR Template

```markdown
**Description**
Brief description of changes.

**Type of Change**
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

**Testing**
- [ ] Tested on Windows
- [ ] Tested on Linux
- [ ] Tested on macOS

**Checklist**
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
```

## Coding Standards

### Python Style Guide

```python
# Good: Descriptive function names
def rename_files_in_range(start, end, prefix):
    """
    Rename files within a specified range.
    
    Args:
        start (int): Starting number
        end (int): Ending number
        prefix (str): File prefix
        
    Returns:
        list: List of renamed files
    """
    pass

# Good: Clear variable names
file_count = len(files)
current_directory = os.getcwd()

# Good: Error handling
try:
    os.rename(old_path, new_path)
except OSError as e:
    print(f"Error renaming file: {e}")
    return False
```

### Best Practices

1. **Functions**: Keep them small and focused
2. **Comments**: Explain why, not what
3. **Error Handling**: Always handle exceptions gracefully
4. **Logging**: Use the log_action function for important operations
5. **User Input**: Always validate and sanitize

## Testing Guidelines

### Manual Testing Checklist

Before submitting a PR, test these scenarios:

```bash
# Basic functionality
python r3namex.py -h
python r3namex.py -v
python r3namex.py -u

# Rename operations
python r3namex.py -l test_folder -p Test -cs 1 -ce 5 -ns 10
python r3namex.py -l test_folder -a
python r3namex.py -l test_folder -r

# Edge cases
# - Empty folders
# - Files without extensions
# - Unicode filenames
# - Very long filenames
# - Permission errors
```

### Test File Structure

Create a test directory:
```
test_files/
├── File1.txt
├── File2.txt
├── File3.jpg
├── subfolder/
│   ├── Doc1.pdf
│   └── Doc2.pdf
└── empty_folder/
```

## Documentation

### Docstring Format

```python
def function_name(param1, param2):
    """
    Brief description of function.
    
    Longer description if needed, explaining the purpose
    and any important details.
    
    Args:
        param1 (type): Description of param1
        param2 (type): Description of param2
        
    Returns:
        type: Description of return value
        
    Raises:
        ExceptionType: When this exception occurs
        
    Example:
        >>> function_name("test", 123)
        "result"
    """
```

### README Updates

When adding features, update:
- Feature list
- Usage examples
- Options reference
- FAQ/Troubleshooting if needed

## Community

### Getting Help

- **Issues**: Check existing issues or create new ones
- **Discussions**: Use GitHub Discussions for questions
- **Email**: @stuxboynet in x.com (for security issues only)

### Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in commit messages

## Version Numbering

We use Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

## Release Process

1. Update version in `r3namex.py`
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release
5. Update README if needed

---

## Quick Contribution Checklist

- [ ] Read this guide
- [ ] Check existing issues
- [ ] Fork and branch
- [ ] Write clean code
- [ ] Test thoroughly
- [ ] Update docs
- [ ] Submit PR
- [ ] Respond to feedback

Thank you for contributing to R3nameX! 🚀
