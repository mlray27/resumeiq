name: JobAgent — 3x Daily

on:
  schedule:
    - cron: '0 14 * * *'   # 9AM EST  (UTC-5)
    - cron: '0 19 * * *'   # 2PM EST
    - cron: '0 0 * * *'    # 7PM EST
  workflow_dispatch:         # manual trigger anytime

jobs:
  run-agent:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          cd jobagent
          pip install -r requirements.txt

      - name: Run JobAgent
        env:
          GEMINI_API_KEY:  ${{ secrets.GEMINI_API_KEY }}
          GMAIL_USER:      ${{ secrets.GMAIL_USER }}
          GMAIL_APP_PASS:  ${{ secrets.GMAIL_APP_PASS }}
          SERPAPI_KEY:     ${{ secrets.SERPAPI_KEY }}
        run: |
          cd jobagent
          mkdir -p results
          python agent.py

      - name: Commit results for dashboard
        run: |
          git config --global user.name  "JobAgent Bot"
          git config --global user.email "bot@jobagent"
          git add jobagent/results/
          git diff --staged --quiet || git commit -m "chore: job results $(date +'%Y-%m-%d %H:%M')"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
