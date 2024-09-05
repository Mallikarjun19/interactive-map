from flask import Flask,request, jsonify
import geemap
import ee
from IPython.display import display
from ipywidgets import Output
import ipywidgets as widgets

app = Flask(__name__)

# Initialize Earth Engine
ee.Initialize(project='ee-top1')
@app.route('/getNDVI', methods=['GET'])
def get_ndvi():
    try:
        # Get the polygon coordinates from the request
        polygon_coords = request.args.get('polygon')
        if not polygon_coords:
            return jsonify({'error': 'Polygon coordinates are missing'}), 400
        coords = [list(map(float, coord.split(','))) for coord in polygon_coords.split(';')]
        
        # Create an Earth Engine polygon geometry
        polygon = ee.Geometry.Polygon(coords)

        # Get the NDVI dataset and calculate the mean NDVI
        ndvi = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filterDate('2022-01-01', '2022-08-01') \
            .map(lambda image: image.normalizedDifference(['B8', 'B4']).rename('NDVI')) \
            .mean()
        
        # Clip the NDVI image to the polygon
        ndvi_clipped = ndvi.clip(polygon)

        # Calculate the mean NDVI for the polygon
        mean_ndvi = ndvi_clipped.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=polygon,
            scale=10
        ).get('NDVI').getInfo()

        # Return the result as JSON
        return jsonify({'ndvi': mean_ndvi})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)