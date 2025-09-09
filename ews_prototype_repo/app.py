
from flask import Flask, jsonify, send_file, request
import pandas as pd, os
from datetime import datetime

BASE = os.path.dirname(__file__)
DATA_CSV = os.path.join(BASE, 'ews_demo.csv')

app = Flask(__name__, static_folder='static', template_folder='static')

def latest_snapshot():
    df = pd.read_csv(DATA_CSV, parse_dates=['timestamp'])
    last = df.iloc[-1].to_dict()
    # convert numpy types
    for k,v in last.items():
        try:
            if isinstance(v, (pd.Timestamp,)):
                last[k] = v.isoformat()
        except:
            pass
    return last

@app.route('/')
def index():
    return send_file(os.path.join(BASE, 'static', 'index.html'))

@app.route('/status')
def status():
    last = latest_snapshot()
    return jsonify({
        'timestamp': last['timestamp'],
        'phase': last['phase'],
        'CAI': float(last['CAI']),
        'CDI': float(last['CDI']),
        'THI': float(last['THI']),
        'TI': float(last['TI']),
        'EI': float(last['EI']),
        'ATI': float(last['ATI']),
        'SNI': float(last['SNI']),
        'PCI': float(last['PCI']),
        'BI': float(last['BI']),
        'Risk': float(last['Risk']),
        'Alert': last['Alert']
    })

@app.route('/history')
def history():
    n = int(request.args.get('n', 288))  # default: 24h at 5-min = 288
    df = pd.read_csv(DATA_CSV, parse_dates=['timestamp'])
    df = df.tail(n)
    # Remove RiskExtended if present to keep strictly Risk-only stream
    if 'RiskExtended' in df.columns:
        df = df.drop(columns=['RiskExtended'])
    return df.to_json(orient='records', date_format='iso')

@app.route('/plot')
def plot():
    img = os.path.join(BASE, 'ews_plot.png')
    if os.path.exists(img):
        return send_file(img, mimetype='image/png')
    return ('Not found', 404)

@app.route('/download/<path:fname>')
def download(fname):
    # sanitize
    allowed = ['ews_demo.csv', 'ews_demo.xlsx', 'ews_plot.png', 'ews_model.py']
    if fname not in allowed:
        return ('Not allowed', 403)
    return send_file(os.path.join(BASE, fname), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
