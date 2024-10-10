import pandas as pd

# Load the combined stops data
all_stops = pd.read_csv("all_routes_stops.csv")

# Load the routes data to get route_long_name
routes_data = pd.read_csv('stcp data/routes.txt')

# Extract route_id from the route column (characters before the first underscore)
all_stops['route_id'] = all_stops['route'].str.split('_').str[0]

# Merge the all_stops DataFrame with routes_data to get route_long_name
all_stops = all_stops.merge(routes_data[['route_id', 'route_long_name']], on='route_id', how='left')

# Rename columns
all_stops.rename(columns={
    'route_id': 'route',
    'route_long_name': 'route_name',
    'route': 'route_shape_id'
}, inplace=True)

# Reorder columns to have 'route' as the first column and 'route_name' as the second
all_stops = all_stops[['route', 'route_name'] + [col for col in all_stops.columns if col not in ['route', 'route_name']]]

# Save the updated DataFrame to a new CSV file
all_stops.to_csv("updated_all_routes_stops.csv", index=False)
