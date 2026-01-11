#!/usr/bin/env python3
"""
Build script for Models Got Talent static site.

Loads experiment results from CSV or pickle, processes the data,
and generates a static HTML site with a searchable table.
"""

import os
import sys
import pandas as pd
from pathlib import Path

def load_experiment_data(data_path):
    """Load experiment data from CSV or pickle file."""
    if not os.path.exists(data_path):
        print(f"Error: Data file not found: {data_path}")
        sys.exit(1)

    file_ext = Path(data_path).suffix.lower()

    if file_ext == '.csv':
        df = pd.read_csv(data_path)
    elif file_ext == '.pkl' or file_ext == '.pickle':
        df = pd.read_pickle(data_path)
    else:
        print(f"Error: Unsupported file format: {file_ext}. Use .csv or .pkl/.pickle")
        sys.exit(1)

    print(f"Loaded {len(df)} experiments from {data_path}")
    return df

def sanitize_and_select_columns(df):
    """Select and sanitize columns for the public site."""
    # Define the columns we want to keep
    desired_columns = [
        'model_id', 'dataset', 'model_family', 'model_type',
        'best_val_accuracy', 'best_test_accuracy', 'val_loss', 'test_loss',
        'parameter_count', 'training_time_hours'
    ]

    # Check which columns are available
    available_columns = [col for col in desired_columns if col in df.columns]

    if len(available_columns) < len(desired_columns):
        missing = set(desired_columns) - set(available_columns)
        print(f"Warning: Missing columns: {missing}")
        print(f"Available columns: {list(df.columns)}")

    # Select available columns
    df_selected = df[available_columns].copy()

    # Sanitize data types and handle missing values
    numeric_columns = ['best_val_accuracy', 'best_test_accuracy', 'val_loss', 'test_loss',
                      'parameter_count', 'training_time_hours']

    for col in numeric_columns:
        if col in df_selected.columns:
            df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')

    # Fill missing values with appropriate defaults
    df_selected = df_selected.fillna({
        'best_val_accuracy': 0.0,
        'best_test_accuracy': 0.0,
        'val_loss': float('inf'),
        'test_loss': float('inf'),
        'parameter_count': 0,
        'training_time_hours': 0.0
    })

    # Ensure model_id is string and not empty
    df_selected['model_id'] = df_selected['model_id'].astype(str).str.strip()
    df_selected = df_selected[df_selected['model_id'] != '']

    # Sort by best_test_accuracy descending for better default ordering
    if 'best_test_accuracy' in df_selected.columns:
        df_selected = df_selected.sort_values('best_test_accuracy', ascending=False)

    print(f"Selected {len(df_selected)} models with {len(df_selected.columns)} columns")
    return df_selected

def generate_html(df, output_path):
    """Generate the static HTML page."""
    # Get column information for the table
    columns = list(df.columns)

    # Build column definitions for DataTables
    column_defs = ",".join(f'{{ title: "{col.replace("_", " ").title()}" }}' for col in columns)
    table_headers = "".join(f"<th>{col.replace('_', ' ').title()}</th>" for col in columns)

    # Build JavaScript array for columns
    js_columns_array = str(columns).replace("'", '"')

    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Models Got Talent - Experiment Results</title>

    <!-- DataTables CSS -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">

    <!-- Custom styles -->
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px;
            padding: 15px;
            background: #ecf0f1;
            border-radius: 5px;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }}

        .stat-label {{
            font-size: 14px;
            color: #7f8c8d;
            margin-top: 5px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .model-link {{
            color: #3498db;
            text-decoration: none;
        }}

        .model-link:hover {{
            text-decoration: underline;
        }}

        .dataTables_wrapper {{
            margin-top: 20px;
        }}

        .dataTables_filter {{
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Models Got Talent</h1>

        <div class="stats">
            <div class="stat">
                <div class="stat-number">{len(df)}</div>
                <div class="stat-label">Total Models</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(df['dataset'].unique()) if 'dataset' in df.columns else 0}</div>
                <div class="stat-label">Datasets</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(df['model_family'].unique()) if 'model_family' in df.columns else 0}</div>
                <div class="stat-label">Model Families</div>
            </div>
            <div class="stat">
                <div class="stat-number">{df['parameter_count'].max()/1e6:.1f}M</div>
                <div class="stat-label">Max Parameters</div>
            </div>
        </div>

        <table id="models-table" class="display">
            <thead>
                <tr>
                    {table_headers}
                </tr>
            </thead>
            <tbody>
                <!-- Data will be loaded via JavaScript -->
            </tbody>
        </table>
    </div>

    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>

    <!-- DataTables JS -->
    <script type="text/javascript" src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>

    <!-- PapaParse for CSV parsing -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>

    <script>
        $(document).ready(function() {{
            // Load CSV data
            Papa.parse('data/models.csv', {{
                download: true,
                header: true,
                complete: function(results) {{
                    if (results.errors.length > 0) {{
                        console.error('CSV parsing errors:', results.errors);
                        return;
                    }}

                    // Process the data
                    var processedData = results.data.map(function(row) {{
                        var processedRow = [];

                        // Process each column
                        {js_columns_array}.forEach(function(col) {{
                            var value = row[col];

                            // Special handling for model_id - make it a link
                            if (col === 'model_id' && value) {{
                                processedRow.push('<a href="#" class="model-link" onclick="showModelDetails(\'' + value + '\')">' + value + '</a>');
                            }}
                            // Format numeric values
                            else if (['best_val_accuracy', 'best_test_accuracy'].includes(col) && !isNaN(value)) {{
                                processedRow.push((parseFloat(value) * 100).toFixed(2) + '%');
                            }}
                            else if (['val_loss', 'test_loss'].includes(col) && !isNaN(value)) {{
                                processedRow.push(parseFloat(value).toFixed(4));
                            }}
                            else if (col === 'parameter_count' && !isNaN(value)) {{
                                var count = parseInt(value);
                                if (count >= 1000000) {{
                                    processedRow.push((count / 1000000).toFixed(1) + 'M');
                                }} else if (count >= 1000) {{
                                    processedRow.push((count / 1000).toFixed(1) + 'K');
                                }} else {{
                                    processedRow.push(count.toString());
                                }}
                            }}
                            else if (col === 'training_time_hours' && !isNaN(value)) {{
                                processedRow.push(parseFloat(value).toFixed(1) + 'h');
                            }}
                            else {{
                                processedRow.push(value || '');
                            }}
                        }});

                        return processedRow;
                    }});

                    // Initialize DataTable
                    $('#models-table').DataTable({{
                        data: processedData,
                        columns: [
                            {column_defs}
                        ],
                        pageLength: 25,
                        order: [[4, 'desc']], // Sort by test accuracy by default
                        responsive: true,
                        dom: '<"top"f>rt<"bottom"lp><"clear">',
                        language: {{
                            search: "Search models:",
                            lengthMenu: "Show _MENU_ models per page",
                            info: "Showing _START_ to _END_ of _TOTAL_ models",
                            infoEmpty: "No models found",
                            infoFiltered: "(filtered from _MAX_ total models)"
                        }}
                    }});
                }},
                error: function(error) {{
                    console.error('Error loading CSV:', error);
                    $('#models-table').html('<tr><td colspan="{len(columns)}">Error loading data. Please check the console for details.</td></tr>');
                }}
            }});
        }});

        function showModelDetails(modelId) {{
            // Placeholder for model detail functionality
            alert('Model details for: ' + modelId + '\\n\\n(This will be implemented to show detailed model information)');
        }}
    </script>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"Generated HTML page: {output_path}")

def main():
    """Main build function."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Input data path (try CSV first, then pickle)
    data_paths = [
        project_root / 'experiment_results.csv',
        project_root / 'experiment_results.pkl',
        project_root / 'experiment_results.pickle'
    ]

    data_path = None
    for path in data_paths:
        if path.exists():
            data_path = path
            break

    if not data_path:
        print("Error: No experiment data file found. Expected one of:")
        for path in data_paths:
            print(f"  {path}")
        sys.exit(1)

    # Output paths
    site_dir = project_root / 'site'
    data_dir = site_dir / 'data'
    output_csv = data_dir / 'models.csv'
    output_html = site_dir / 'index.html'

    # Ensure output directories exist
    data_dir.mkdir(parents=True, exist_ok=True)

    # Load and process data
    df = load_experiment_data(data_path)
    df_processed = sanitize_and_select_columns(df)

    # Save processed data
    df_processed.to_csv(output_csv, index=False)
    print(f"Saved processed data to: {output_csv}")

    # Generate HTML
    generate_html(df_processed, output_html)

    print(f"\nBuild complete! Site generated in: {site_dir}")
    print("To deploy to GitHub Pages, commit and push the /site directory.")

if __name__ == '__main__':
    main()