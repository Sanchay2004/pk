from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__, static_url_path='/static')

# Load the data
df = pd.read_csv("data.csv")

# Define weights for each metric
weights = {
    'rating(out of 5)': 0.1,
    'number of reviews': 0.2,
    'delivery': 0.3,
    'quality': 0.3,
    'response ': 0.1  # Corrected column name with extra space
}

# Normalize each metric to a scale from 0 to 1
df['rating_normalized'] = df['rating(out of 5)'] / 5
df['reviews_normalized'] = df['number of reviews'] / df['number of reviews'].max()

# Calculate the weighted sum of normalized scores to get the overall reliability score
df['reliability_score'] = df.apply(lambda row: sum(row[str(metric)] * weights[str(metric)] for metric in weights), axis=1)

# Create a new DataFrame with reliability scores added
new_df = df.copy()  # Make a copy of the original DataFrame
new_df['reliability_score'] = df['reliability_score']  # Add reliability scores as a new column

# Remove unnamed columns
new_df = new_df.drop(columns=new_df.columns[new_df.columns.str.contains('Unnamed', case=False)])

# Define weights for ranking
price_weight = 0.4
quality_weight = 0.4
reliability_weight = 0.2

# Define functions for filtering, ranking, and getting recommendations
def filter_suppliers(location, category):
    # Filter suppliers based on user's location and category
    filtered_df = new_df[(new_df['zone'] == location) & (new_df['category of tmt bar company'] == category)]
    return filtered_df

def rank_suppliers(filtered_df):
    # Calculate rank score for each supplier
    filtered_df.loc[:, 'rank_score'] = (
        price_weight * (1 - filtered_df['price/kg(rupee)'] / filtered_df['price/kg(rupee)'].max()) +
        quality_weight * filtered_df['quality'] +
        reliability_weight * filtered_df['reliability_score'])

    # Sort suppliers by rank score
    ranked_df = filtered_df.sort_values(by='rank_score', ascending=False)
    return ranked_df

def get_recommendations(location, category, top_n=5):
    # Filter suppliers
    filtered_df = filter_suppliers(location, category)

    # Rank suppliers
    ranked_df = rank_suppliers(filtered_df)

    # Select only specified columns
    recommendations = ranked_df.head(top_n)[['steel supplier', 'city', 'state', 'price/kg(rupee)', 'reliability_score']]
    return recommendations

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user input from the form
        category = int(request.form['category'])
        zone = request.form['zone']

        # Call the recommender system function to get recommendations
        recommendations = get_recommendations(zone, category)

        # Return recommendations as JSON response
        return jsonify({'recommendations': recommendations.to_dict(orient='records')})
    else:
        return render_template('index.html', recommendations=None)

@app.route('/page1')
def page1():
    return render_template('page1.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')

if __name__ == '__main__':
    app.run(debug=True)
