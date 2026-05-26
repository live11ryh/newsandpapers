# Daily Science & Technology News Report Setup Guide

## Overview
This project automatically collects 20 important science and technology news items daily and sends them to your email at 9 AM UTC.

## Prerequisites
- GitHub repository (this one)
- Gmail account (for sending emails)
- NewsAPI key (optional, for more news sources)

## Step-by-Step Setup

### 1. Get a Gmail App Password
Since Gmail requires app passwords for third-party applications:

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **Security** in the left menu
3. Enable **2-Step Verification** (if not already enabled)
4. Go back to Security, find **App passwords**
5. Select **Mail** and **Windows Computer**
6. Google will generate a 16-character password - copy it

### 2. Get NewsAPI Key (Optional but Recommended)
1. Visit [newsapi.org](https://newsapi.org)
2. Sign up for a free account
3. Copy your API key from the dashboard

### 3. Configure GitHub Secrets

Go to your repository Settings → Secrets and variables → Actions and add these secrets:

| Secret Name | Value | Required |
|------------|-------|----------|
| `EMAIL_ADDRESS` | Your Gmail address | Yes |
| `EMAIL_PASSWORD` | Your Gmail app password (16 chars) | Yes |
| `RECIPIENT_EMAIL` | Email to receive reports (can be same as above) | Yes |
| `NEWS_API_KEY` | Your NewsAPI key | No |

**Steps to add secrets:**
1. Go to `https://github.com/live11ryh/newsandpapers/settings/secrets/actions`
2. Click **New repository secret**
3. Enter name and value
4. Click **Add secret**

### 4. Verify the Workflow

1. Go to the **Actions** tab in your repository
2. You should see "Daily Science & Tech News Report" workflow
3. Click **Run workflow** to test immediately
4. Check your email for the report

### 5. Adjust Schedule (Optional)

If you want to change the time or frequency:

1. Edit `.github/workflows/daily-news.yml`
2. Modify the cron expression in the `schedule` section:
   ```yaml
   - cron: '0 9 * * *'  # Currently 9 AM UTC every day
   ```
3. Cron format: `minute hour day month weekday`
   - `0 9 * * *` = 9:00 AM UTC daily
   - `0 14 * * 1-5` = 2:00 PM UTC Mon-Fri
   - `0 21 * * *` = 9:00 PM UTC daily

### 6. View Collected News

- News is saved to `data/news_YYYY-MM-DD.json`
- Each day creates a new file with that day's 20 news items
- You can view these in the repository

## News Sources

The script collects from:
1. **NewsAPI** - Global news across 50+ sources
2. **Hacker News** - Tech and science community curated stories

## Troubleshooting

### Email not received?
- Check GitHub Actions logs: Actions tab → workflow run
- Verify Gmail app password (not your regular password)
- Check spam/junk folder
- Ensure RECIPIENT_EMAIL is set in secrets

### "Email credentials not configured" error?
- Make sure all three email secrets are set: `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `RECIPIENT_EMAIL`

### No news items collected?
- Check if NEWS_API_KEY is set (optional but improves results)
- Check GitHub Actions logs for API errors

### Want to test immediately?
- Go to Actions tab
- Click "Daily Science & Tech News Report"
- Click "Run workflow"

## Customization

### Change number of news items
Edit `scripts/collect_and_send_news.py` and change:
```python
NEWS_PER_REPORT = 20  # Change this number
```

### Add more news sources
Edit the script to include:
- RSS feeds (add `feedparser` parsing)
- ArXiv (for research papers)
- Medium, Dev.to (for tech blogs)
- Reddit (for community discussions)

### Modify email format
Edit `format_email_body()` function in `scripts/collect_and_send_news.py`

## Important Notes

⚠️ **Security:**
- Never commit your passwords or API keys to the repository
- Always use GitHub Secrets for sensitive information
- The Gmail app password is different from your account password

⚠️ **Gmail Limits:**
- Free Gmail allows 500 emails/day
- That's plenty for one daily report
- If you need more, consider SendGrid or other email services

## Support

If you encounter issues:
1. Check GitHub Actions logs (Actions tab → workflow run)
2. Look at the error message
3. Check this guide's Troubleshooting section

Happy reading! 📰🔬
