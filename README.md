# combolist-check
Combolist-check is a program designed to search one or more combolists for specific domains or email addresses, remove duplicate entries, and generate a CSV file with the findings in a structured format.

## Features
# 1. Targeted Search
Search Criteria:
- One or more domains.
- A specific email address.

# 2. Duplicate Removal
Detects and removes duplicate entries from the search results.

# 3. Results Output
Outputs findings in a CSV file with the following fields:
- email: The email address identified in the combolist.
- password: The associated password.
- email-password: The email-password combination found.
- URL: the associated URL (if present).
- source date: The date of the combolist creation.
- data leak: The specific name of the combolist.
- Tag: Custom or additional tags for classification.

## Usage
python3 combolist_check.py
