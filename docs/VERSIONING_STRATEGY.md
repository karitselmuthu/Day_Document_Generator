# Versioning Strategy for Day Document Generator

## Overview

This repository follows a **date-tagged versioning strategy** where:
- **`main` branch** = Latest production version (always deployable)
- **`vX.Y.Z-YYYY-MM-DD` branches** = Previous versions (preserved for reference)

Every code change creates a new version with a unique date tag.

---

## Current Version Structure

### Active Development
```
main (v2.0.1-2026-08-03)
└─ Latest features: RAG enhancements + documentation
└─ Latest commit: 39f0257 (Add RAG enhancement summary)
```

### Previous Versions (Archived Branches)
```
v2.0.0-2026-08-02
└─ Commit: c683ab1
└─ Features: RAG generators enhancement
└─ Read-only archive branch

v1.1.0-2026-08-01
└─ Commit: 567b61e
└─ Features: README and application documentation
└─ Read-only archive branch

v1.0.0-2026-07-31
└─ Commit: 13487f8
└─ Features: S3 storage with versioning
└─ Read-only archive branch (baseline)
```

---

## Workflow: How to Add New Code

### Step 1: Develop on Main Branch
```bash
cd Day_Document_Generator
git checkout main
git pull origin main

# Make your changes
# Edit files, test thoroughly
```

### Step 2: Commit Changes
```bash
git add .
git commit -m "Clear description of what changed"
```

### Step 3: Tag Previous Version
When you're ready to deploy new code:

```bash
# Get the date of the last commit on main
CURRENT_VERSION="$(git log --format='%ad' -1 --date=format:'%Y-%m-%d')"
LAST_COMMIT="$(git rev-parse HEAD)"

# Create a version branch BEFORE pushing new code
git branch v2.1.0-${CURRENT_VERSION} ${LAST_COMMIT}
git push origin v2.1.0-${CURRENT_VERSION}

# Now push main with latest code
git push origin main
```

### Step 4: Update Version in Documentation
Update `VERSION.txt` or document the new version:
```bash
echo "Current Version: 2.1.1-2026-08-03" > VERSION.txt
git add VERSION.txt
git commit -m "Update version to 2.1.1"
git push origin main
```

---

## Versioning Scheme Explained

### Version Number Format: `vX.Y.Z-YYYY-MM-DD`

- **X.Y.Z** = Semantic versioning
  - **X** = Major version (breaking changes)
  - **Y** = Minor version (new features)
  - **Z** = Patch version (bug fixes)
  
- **YYYY-MM-DD** = Date version was created

### Example Timeline

```
2026-07-31  v1.0.0-2026-07-31  Initial S3 integration
2026-08-01  v1.1.0-2026-08-01  Added README & documentation
2026-08-02  v2.0.0-2026-08-02  Major: RAG enhancements (breaking changes)
2026-08-03  v2.1.0-2026-08-03  New: Additional features
2026-08-04  v2.1.1-2026-08-04  Patch: Bug fix
```

---

## How Main Branch Works

### Main Branch Characteristics
- ✅ Always contains latest code
- ✅ Always deployable (tested)
- ✅ Updated immediately when new features are ready
- ✅ Direct commits to main for quick updates

### Release Checklist
Before pushing to main:
- [ ] Code tested locally
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changes committed
- [ ] Previous version branch created
- [ ] Ready to `git push origin main`

---

## Version Branch Characteristics

### Version Branches (Read-Only Archive)
- ✅ Immutable once created
- ✅ Preserved for historical reference
- ✅ No new commits added
- ✅ Can be checked out for reference or patching old versions
- ✅ Serves as deployment snapshot

---

## Common Tasks

### View Version History
```bash
# See all version branches
git branch -a | grep "^.*v[0-9]"

# See commits in each version
git log v1.0.0-2026-07-31..v1.1.0-2026-08-01 --oneline
```

### Checkout an Old Version
```bash
# To review or debug old version
git checkout v1.0.0-2026-07-31
git log --oneline -5

# Return to main
git checkout main
```

### Cherry-pick from Old Version
```bash
# If you need a specific commit from an old version
git checkout main
git cherry-pick <commit-hash>
git push origin main
```

### Create Patch for Old Version
```bash
# If bug found in v1.0.0, fix it there
git checkout v1.0.0-2026-07-31
git checkout -b v1.0.1-patch-2026-08-03

# Make fix
git commit -m "Fix: bug in old version"
git push origin v1.0.1-patch-2026-08-03

# Merge fix back to main
git checkout main
git cherry-pick <fix-commit>
git push origin main
```

---

## GitHub Interface

### Viewing Versions on GitHub
```
Repository → Branches tab
┌─ main (default)
├─ v2.0.0-2026-08-02
├─ v1.1.0-2026-08-01
└─ v1.0.0-2026-07-31
```

### Release Tags (Optional)
You can create GitHub Releases for versions:
```bash
# Tag a version
git tag -a v2.0.0 -m "Release version 2.0.0: RAG enhancement"
git push origin v2.0.0

# Then create release on GitHub from that tag
# With release notes, files, changelog
```

---

## Integration with GitHub MCP

**No GitHub MCP configuration needed.** This is a local git workflow that automatically works with GitHub.

**How it works:**
1. All branches sync automatically with `git push`
2. GitHub shows all version branches in UI
3. Pull requests can target any branch
4. Release notes can be created per version tag

---

## Recommended Automation

### Create a Script for New Versions
```bash
#!/bin/bash
# create_version.sh

VERSION=$1
DATE=$(date +%Y-%m-%d)
PREVIOUS_COMMIT=$(git rev-parse HEAD)

# Create version branch from current commit
git branch "v${VERSION}-${DATE}" ${PREVIOUS_COMMIT}

# Push version branch
git push origin "v${VERSION}-${DATE}"

# Continue on main for new changes
git checkout main
git push origin main

echo "✅ Created version v${VERSION}-${DATE}"
echo "✅ Pushed to GitHub"
echo "✅ Main branch ready for new changes"
```

Usage:
```bash
./create_version.sh 2.1.0
```

---

## Best Practices

### ✅ DO
- Create a version branch BEFORE pushing new code to main
- Use semantic versioning (X.Y.Z) meaningfully
- Keep main branch stable and deployable
- Document major version changes
- Tag releases on GitHub for easy reference

### ❌ DON'T
- Commit directly to version branches
- Push untested code to main
- Skip creating version branches
- Rebase main (use merge commits)
- Delete old version branches

---

## Workflow Summary

```
New Feature Development
    ↓
Test Locally
    ↓
Commit to main
    ↓
Create version branch: git branch vX.Y.Z-YYYY-MM-DD
    ↓
Push version branch: git push origin vX.Y.Z-YYYY-MM-DD
    ↓
Push main: git push origin main
    ↓
Create GitHub Release (optional)
    ↓
Archive completed (version branch is now read-only)
    ↓
Continue with next feature on main
```

---

## Current Version History

| Version | Date | Branch | Commit | Description |
| --- | --- | --- | --- | --- |
| v2.0.1 | 2026-08-03 | main | 39f0257 | RAG enhancement summary |
| v2.0.0 | 2026-08-02 | v2.0.0-2026-08-02 | c683ab1 | RAG generator enhancements |
| v1.1.0 | 2026-08-01 | v1.1.0-2026-08-01 | 567b61e | README & documentation |
| v1.0.0 | 2026-07-31 | v1.0.0-2026-07-31 | 13487f8 | S3 storage with versioning |

---

## Next New Version Example

When you're ready to add new features:

```bash
# Step 1: Make your changes on main
git checkout main
git pull origin main
# ... edit files ...

# Step 2: Commit
git add .
git commit -m "Add new feature XYZ"

# Step 3: Create version branch BEFORE pushing
git branch v2.1.0-2026-08-04
git push origin v2.1.0-2026-08-04

# Step 4: Push new main
git push origin main

# Step 5: You're done!
# Previous main (v2.0.1) is now archived on v2.0.1-2026-08-03 branch
```

---

## Support

For questions about versioning:
- Review git history: `git log --oneline --graph --all`
- See branch structure: `git branch -a`
- Compare versions: `git diff v1.0.0 v2.0.0`

