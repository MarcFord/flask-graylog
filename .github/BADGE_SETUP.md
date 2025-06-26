# Badge Status and Setup

This document explains the status of the badges in the README and what's needed for them to update properly.

## Current Badge Status

### ✅ Working Badges

1. **CI Badge**: `[![CI](https://github.com/MarcFord/flask-graylog/actions/workflows/ci.yml/badge.svg?branch=main)]`
   - **Status**: Should update automatically with each push to main
   - **Shows**: Latest GitHub Actions workflow status
   - **Updates**: Immediately after workflow completion

2. **Python Version Badge**: `[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)]`
   - **Status**: Static badge, always shows "Python 3.9+"
   - **Shows**: Supported Python versions
   - **Updates**: Manual update only

3. **License Badge**: `[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]`
   - **Status**: Static badge based on LICENSE file
   - **Shows**: Project license (MIT)
   - **Updates**: Automatically if license changes

### 🔄 Pending Setup Badges

4. **Codecov Badge**: `[![codecov](https://codecov.io/gh/MarcFord/flask-graylog/branch/main/graph/badge.svg)]`
   - **Status**: Needs Codecov account setup
   - **Shows**: Test coverage percentage
   - **Required Steps**:
     1. Sign up at https://codecov.io with your GitHub account
     2. Add the `MarcFord/flask-graylog` repository
     3. The badge will update automatically after the first coverage upload

## Future Badges (After PyPI Release)

These badges will work after your first PyPI release:

```markdown
[![PyPI version](https://badge.fury.io/py/flask-graylog.svg)](https://badge.fury.io/py/flask-graylog)
[![PyPI downloads](https://img.shields.io/pypi/dm/flask-graylog.svg)](https://pypi.org/project/flask-graylog/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flask-graylog)](https://pypi.org/project/flask-graylog/)
```

## Codecov Setup Instructions

### Step 1: Sign Up
1. Go to https://codecov.io
2. Click "Sign up with GitHub"
3. Authorize Codecov to access your repositories

### Step 2: Add Repository
1. In your Codecov dashboard, click "Add new repository"
2. Find and select `MarcFord/flask-graylog`
3. Follow the setup instructions

### Step 3: Verify Upload
1. Push a commit to trigger the CI workflow
2. Check the workflow logs for successful coverage upload
3. Visit https://codecov.io/gh/MarcFord/flask-graylog to see coverage reports

## Troubleshooting

### Workflow Parsing Errors
- **Issue**: "workflow is not reusable as it is missing a `on.workflow_call` trigger"
- **Solution**: ✅ **FIXED** - Added `workflow_call` trigger to CI workflow
- **Details**: The release workflow calls the CI workflow, which now supports reusable workflow calls

### CI Badge Not Updating
- Check that the workflow file is named exactly `ci.yml`
- Ensure the workflow is triggered on push to main branch
- Verify the badge URL matches your repository and workflow name

### Codecov Badge Shows "unknown"
- Ensure you've signed up for Codecov and added the repository
- Check that coverage.xml is being generated in CI
- Verify the codecov upload step is running successfully
- Look for error messages in the CI workflow logs

### Badge Caching
- Badges may be cached by GitHub/browsers for a few minutes
- Try refreshing the page or opening in an incognito window
- GitHub badge cache typically updates within 5-10 minutes

## Current CI Workflow Coverage Upload

The CI workflow is configured to:
1. Run tests with coverage on Ubuntu + Python 3.11
2. Generate `coverage.xml` file
3. Upload coverage to Codecov (tokenless for public repos)
4. List generated files for debugging

The workflow should work automatically once you've set up Codecov.
