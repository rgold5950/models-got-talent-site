# Models Got Talent - Static Site

A static GitHub Pages site for displaying machine learning experiment results in an interactive, searchable table.

## Overview

This repository contains a static site generator that creates a searchable, sortable, filterable table of ML experiment results. The site uses:

- **DataTables** for table functionality (search, sort, filter, pagination)
- **PapaParse** for client-side CSV parsing
- **Pure static HTML/CSS/JavaScript** - no backend required

## Directory Structure

```
├── experiment_results.csv          # Input data (CSV or .pkl/.pickle)
├── tools/
│   └── build_site.py              # Site generation script
└── site/                          # Generated static site (GitHub Pages root)
    ├── index.html                 # Main page
    └── data/
        └── models.csv            # Processed data for the table
```

## Quick Start

1. **Prepare your data**: Create `experiment_results.csv` or `experiment_results.pkl` with your experiment results.

2. **Run the build script**:
   ```bash
   python tools/build_site.py
   ```

3. **Deploy to GitHub Pages**: Commit and push the `/site` directory to deploy the live site.

## Data Format

The build script expects experiment data with these columns (all optional):

- `model_id`: Unique identifier for each model (will become clickable links)
- `dataset`: Dataset name
- `model_family`: High-level model category (e.g., "transformer", "cnn")
- `model_type`: Specific model type/architecture
- `best_val_accuracy`: Best validation accuracy (0-1 scale)
- `best_test_accuracy`: Best test accuracy (0-1 scale)
- `val_loss`: Validation loss
- `test_loss`: Test loss
- `parameter_count`: Number of parameters
- `training_time_hours`: Training time in hours

## Features

### Table Functionality
- **Search**: Global search across all columns
- **Sort**: Click column headers to sort
- **Filter**: Built-in filtering capabilities
- **Pagination**: Navigate through results
- **Responsive**: Works on mobile devices

### Data Formatting
- Model IDs rendered as clickable links (placeholder for future detail pages)
- Accuracies shown as percentages
- Parameter counts formatted (K/M suffixes)
- Training times shown with hours suffix

### Statistics Dashboard
- Total number of models
- Number of unique datasets
- Number of model families
- Maximum parameter count

## Customization

### Modifying Columns
Edit the `desired_columns` list in `tools/build_site.py` to include/exclude columns from your data.

### Styling
Modify the CSS in the generated `index.html` or edit the template in `build_site.py`.

### Data Processing
Customize the `sanitize_and_select_columns()` function in `build_site.py` for data preprocessing.

## GitHub Pages Setup

1. **Repository Settings**: Go to Settings → Pages
2. **Source**: Select "Deploy from a branch"
3. **Branch**: Choose `main` (or your default branch)
4. **Folder**: Select `/site`
5. **Save**

The site will be available at `https://[username].github.io/[repository-name]/`

## Development

### Testing Locally
Open `site/index.html` in a web browser to test the site locally.

### Regenerating the Site
Run the build script whenever your experiment data changes:

```bash
python tools/build_site.py
```

### Adding Model Detail Pages
The model IDs are currently placeholders. To add detail pages:

1. Create individual HTML files in `/site/models/[model_id].html`
2. Update the `showModelDetails()` JavaScript function to navigate to these pages

## Dependencies

- Python 3.6+
- pandas (for data processing)

Install dependencies:
```bash
pip install pandas
```

## License

[Add your license information here]