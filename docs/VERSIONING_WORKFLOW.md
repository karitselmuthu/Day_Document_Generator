# Version Branch Workflow

## Problem Identified ❌

Today (2026-08-03), **3+ commits** were made to `main`:
- ✓ Organize MD files into docs folder (5ef36ad)
- ✓ Refactor folder structure to use DD_MM_YY (92fba80)

But **NO VERSION BRANCH** was created for today!

### Expected vs Actual
```
Expected:
  v1.0.0-2026-07-31
  v1.1.0-2026-08-01
  v2.0.0-2026-08-02
  v2.0.1-2026-08-03 ← MISSING! ❌

Actual:
  v1.0.0-2026-07-31
  v1.1.0-2026-08-01
  v2.0.0-2026-08-02
  (nothing for 2026-08-03)
```

---

## Solution: Versioning Workflow

### Pattern Used

**Semantic Versioning + Date:** `v{MAJOR}.{MINOR}.{PATCH}-{DD_MM_YY}`

| When | Version Changes | Example |
|------|-----------------|---------|
| New Day | Minor bump | v1.0.0 → v1.1.0 (next day) |
| Same Day | Patch bump | v2.0.0 → v2.0.1 (same day) |
| Major Changes | Major bump | v1.x.x → v2.x.x (breaking changes) |

### Existing Version History
```
v1.0.0-2026-07-31  (July 31)   - Initial release
v1.1.0-2026-08-01  (Aug 1)     - First feature update (new day)
v2.0.0-2026-08-02  (Aug 2)     - Major version bump + new day
v2.0.1-2026-08-03  (Aug 3)     - Patch update + new day ← NOW CREATED ✓
```

---

## How to Create Version Branch

### Option 1: Automatic Script (Recommended)

```bash
# Run after making commits to main
./create-version-branch.sh

# Output:
# Creating version branch for today (2026-08-03)
# Branch name: v2.0.1-2026-08-03
# ✓ Version branch created and pushed successfully!
```

### Option 2: Manual Command

```bash
# Create version branch
git checkout -b v2.0.1-2026-08-03

# Push to GitHub
git push origin v2.0.1-2026-08-03

# Switch back to main
git checkout main
```

### Option 3: Custom Version (for major changes)

```bash
# If you're making breaking changes, bump major version
./create-version-branch.sh v3.0.0

# This creates: v3.0.0-2026-08-03
```

---

## Workflow Steps (Daily)

### Morning: Start New Day
```bash
# Pull latest from main
git checkout main
git pull origin main
```

### During Day: Make Changes
```bash
# Make code changes
git add .
git commit -m "Your feature description"
git push origin main

# Repeat for multiple commits...
git add .
git commit -m "Another feature"
git push origin main
```

### End of Day: Create Version Branch
```bash
# After all commits for the day
./create-version-branch.sh

# This will:
# 1. Auto-detect version (increment patch if same day, minor if new day)
# 2. Create branch with today's date
# 3. Push to GitHub
# 4. Keep main as-is for tomorrow's work
```

---

## Branch Structure on GitHub

### After Today's Version Creation

```
main (always the latest code)
  └─ Contains: all commits from all days
  └─ Points to: Latest commit (92fba80)

v2.0.1-2026-08-03 (today's version snapshot)
  └─ Contains: Same as main at point of branch creation
  └─ Points to: Latest commit of today (92fba80)
  └─ Purpose: Historical record of today's release

v2.0.0-2026-08-02 (yesterday's version snapshot)
  └─ Contains: All code as of yesterday
  └─ Points to: Last commit of yesterday
  └─ Purpose: Can roll back to this if needed

v1.1.0-2026-08-01
  └─ Similar structure for Aug 1

v1.0.0-2026-07-31
  └─ Similar structure for July 31
```

---

## Why This Matters

### ✅ Benefits

| Benefit | How |
|---------|-----|
| **Version Tracking** | Every day has a snapshot branch |
| **Easy Rollbacks** | Can checkout v2.0.0-2026-08-02 anytime |
| **Release Management** | Tag branches for production deployments |
| **Audit Trail** | Clear history of what changed each day |
| **Team Communication** | Everyone knows which version is current |

### ❌ Without Versioning

- All commits blend into main
- Can't tell what was in "yesterday's release"
- Hard to rollback to a specific day
- No clear deployment history
- Team confusion about versions

---

## Semantic Versioning Guide

### When to Bump Each Level

**MAJOR (v2.0.0 → v3.0.0)**
- Breaking API changes
- Major refactoring
- Incompatible with previous versions
- Example: Changing folder structure from day1/day2 to DD_MM_YY ✓ (This was v2.0.0)

**MINOR (v2.0.0 → v2.1.0)**
- New features added
- New day of work with multiple features
- Backward compatible
- Example: Adding PDF support (v1.1.0), Adding RAG ecosystem (v2.0.0)

**PATCH (v2.0.0 → v2.0.1)**
- Bug fixes
- Small improvements
- Multiple commits same day
- Example: Today's MD reorganization + folder structure refactor

---

## GitHub Commands for Version Management

### View All Version Branches
```bash
git branch -r | grep "origin/v"
```

### Switch to a Previous Version
```bash
git checkout v2.0.0-2026-08-02
```

### Create Tag (Additional, Optional)
```bash
git tag -a v2.0.1-2026-08-03 -m "Release notes here"
git push origin v2.0.1-2026-08-03
```

### See Commits in a Version
```bash
git log v2.0.1-2026-08-03..v2.0.0-2026-08-02
```

---

## Post-Today Action Items

- [x] Create v2.0.1-2026-08-03 branch ✓
- [ ] Next time: Run `./create-version-branch.sh` after all daily commits
- [ ] Document in team wiki/README
- [ ] Set up GitHub Actions to auto-create versions (optional)

---

## Reference

**Current Version Branches:**
```
✓ v1.0.0-2026-07-31  (Initial)
✓ v1.1.0-2026-08-01  (Features)
✓ v2.0.0-2026-08-02  (Major refactor)
✓ v2.0.1-2026-08-03  (Bug fixes & improvements) ← NEW TODAY!
```

**Next Step:** Tomorrow after commits, run `./create-version-branch.sh` again!
