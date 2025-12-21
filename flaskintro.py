from flask import Flask,render_template


app=Flask(__name__)

@app.route("/")
def home():
    return "<h1>first flask app</h1>"

@app.route("/two")
def home2():
    return "is good"

@app.route("/location/<city>")
def future(city):
    return "Bought a home in "+city

@app.route("/form")
def form():
        return render_template("form.html")

@app.route("/details")
def details():
    name="Lavanya"
    salary=100000
    
    return render_template("stats.html",_name=name,_salary=salary)

@app.route("/success/<perform>")
def score(perform):
     return "the person has performed "+perform+" in life"

if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0",port=8080)

