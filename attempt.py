from flask import Flask,render_template
from datetime import datetime
from lightweight_charts import Chart
import pandas as pd

app = Flask(__name__)

@app.route('/')
def hello_world():
    
        return render_template('R:/Projects/Stock_Prediction/try.html')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5003)
