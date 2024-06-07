@app.route('/cpu-exhaust')
def cpu_exhaust():
    # Simulate CPU intensive process
    count = sum(i*i for i in range(10000000))
    return {'result': count}

@app.route('/api-delay')
def api_delay():
    # Simulate delay due to bugs or scheduling issues
    time.sleep(5)  # 5 seconds delay
    return {'status': 'delayed response'}

@app.route('/slow-sql')
def slow_sql():
    # Running a slow SQL query
    result = db.session.execute("SELECT * FROM generate_series(1,1000000) s JOIN big_table b ON s=s.id;")
    db.session.commit()
    return {'status': 'slow query executed'}
