---
status: testing
phase: 04-ai-analysis
source: 04-01-SUMMARY.md, 04-02-SUMMARY.md, 04-03-SUMMARY.md, 04-04-SUMMARY.md, 04-05-SUMMARY.md, 04-06-SUMMARY.md, 04-07-SUMMARY.md, 04-08-SUMMARY.md, 04-09-SUMMARY.md
started: 2026-02-21T18:30:00Z
updated: 2026-02-21T18:30:00Z
---

## Current Test

number: 1
name: All 5 posts display with complete analysis data
expected: |
  When you create a new scan and it completes, you see 5 viral posts displayed.
  Each post shows:
  - Post thumbnail/preview
  - Creator name and follower count
  - Engagement metrics (likes, comments, saves, shares)
  - Viral score badge showing "Exceptional Viral" 100/100
  - "Why It Went Viral" summary (2-3 sentence explanation)
  - Algorithm Factor Badges displayed in a grid showing scores for:
    * Hook Strength (should be 100)
    * Posting Time (should be 60)
    * Engagement Velocity (should be 100)
    * Save/Share Ratio (should be 100)
    * Hashtag Performance (should be 60)
    * Audience Retention (should be 100)
  - Emotional Trigger badge showing the detected emotion (e.g., "Awe")

awaiting: user response

## Tests

### 1. All 5 posts display with complete analysis data
expected: Each post in the scan shows viral score badge, why viral summary, and 6 algorithm factor badges with color-coded scores
result: [pending]

### 2. Algorithm factor badges show correct color coding
expected: Algorithm scores display with proper colors - green for high scores (70+), yellow for medium (40-70), red for low (<40)
result: [pending]

### 3. No errors when fetching analysis for each post
expected: When you click on individual posts, no error messages appear. Analysis displays cleanly without console errors.
result: [pending]

### 4. Analysis data matches expected ranges
expected: All algorithm factor scores are between 0-100. Confidence score visible and between 0-100%. All emotional triggers are valid (Awe, Joy, Surprise, etc.)
result: [pending]

### 5. Loading states display correctly
expected: When analysis first loads, "Loading analysis..." message briefly appears before data displays
result: [pending]

### 6. Analysis displays immediately for previously analyzed posts
expected: If you create another scan with the same posts (cache hit), analysis displays instantly without waiting
result: [pending]

### 7. Emotional triggers display in correct format
expected: Emotional trigger shown in purple badge with capitalized emotion name (e.g., "Awe", "Joy", "Anger")
result: [pending]

### 8. Why viral summary is readable and informative
expected: Summary text explains why post went viral in 2-3 sentences, mentions engagement velocity and viewer appeal patterns
result: [pending]

### 9. No "/100" suffix appears on scores
expected: Algorithm factor badges show just the number (e.g., "100") not "100/100"
result: [pending]

### 10. Font sizes are appropriate and readable
expected: Algorithm factor badge labels and scores are visible and proportionate to the overall layout (not too large, not too small)
result: [pending]

## Summary

total: 10
passed: 0
issues: 0
pending: 10
skipped: 0

## Gaps

[none yet]
