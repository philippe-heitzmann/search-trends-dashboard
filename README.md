# Related Queries Dashboard 
Author: Philippe Heitzmann

## Overview
The Related Queries Dashboard leverages the `trendspy` Python library to fetch trending search queries from the past 24 hours and news articles published on those topics. This project is designed to help news organizations analyze the SEO performance of articles on trending topics to uncover opportunities for optimizing their content. By identifying SEO gaps, the dashboard empowers publishers to strategically target topics for improved visibility and engagement.

---

## Features
- Fetches high-volume trending search queries from the past 24 hours.
- Displays related news articles published on these topics.
- Highlights opportunities to improve SEO performance by analyzing gaps in related articles.

---

### Get Started

To deploy the dashboard locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/philippe-heitzmann/related-queries-dashboard.git
   cd related-queries-dashboard
   ```

2. **Run the Docker Image: Use the provided script to build and run the Docker container**:

    ```bash
    Copy code
    ./src/scripts/build_run.sh
    ```

3. **Access the Dashboard**: 
- Open your browser and navigate to http://localhost:8501 (or the appropriate port specified in the script).**

### Requirements

- Docker: Ensure you have Docker installed on your system to run the project.
- Python (if running locally):
- Python 3.8 or above.
- Dependencies listed in requirements.txt.

