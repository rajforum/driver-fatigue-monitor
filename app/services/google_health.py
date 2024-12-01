from googleapiclient.discovery import build

def get_google_fit_data(credentials):
    service = build('fitness', 'v1', credentials=credentials)
    
    # Example: Fetch activity data
    data_sources = service.users().dataSources().list(userId='me').execute()
    print(data_sources)  # Check available data sources

    # Fetch data from a specific data source (e.g., step count)
    dataset = service.users().dataSources().datasets().get(
        userId='me',
        dataSourceId='derived:com.google.step_count.delta:com.google.android.gms:estimated_steps',
        datasetId='startTime-endTime'
    ).execute()
    
    return dataset
