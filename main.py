from flask import Flask, render_template, request, redirect
import json
import sqlite3
import random

def select_sql(cmd, vals=None):
  conn = sqlite3.connect('flask.db')
  c = conn.cursor()
  if vals:
      res = c.execute(cmd, vals).fetchall()
  else:
      res = c.execute(cmd).fetchall()
  conn.commit()
  conn.close()
  return res

def insert_sql(cmd, vals=None):
   conn = sqlite3.connect('flask.db')
   c = conn.cursor()
   res = c.execute(cmd, vals).fetchall() 
   conn.commit() 
   conn.close()
   return res

app = Flask(__name__)

@app.route("/")
def sakums():
  select_sql("CREATE TABLE IF NOT EXISTS Konts (\
    konts_ID INTEGER PRIMARY KEY AUTOINCREMENT, \
    lietotajvards TEXT NOT NULL, \
    parole TEXT NOT NULL, \
    limenis INT, \
    pieredze INT, \
    speles INT)")
  return render_template("sakums.html")

@app.route("/registret_konts")
def registret_konts():
  return render_template("registret_konts.html")

@app.route("/konts_apstrade", methods=["POST", "GET"]) 
def konts_apstrade():
  registret_konts = {}
  if request.method == "POST":
    registret_konts["lietotajvards"] = request.form["lietotajvards"]
    registret_konts["parole"] = request.form["parole"]
    registret_konts["limenis"] = 1
    registret_konts["pieredze"] = 0
    registret_konts["speles"] = 0
    insert_sql("INSERT INTO Konts (lietotajvards, parole, limenis, pieredze, speles) VALUES (?, ?, ?, ?, ?)" ,[
      registret_konts["lietotajvards"],
      registret_konts["parole"],
      registret_konts["limenis"],
      registret_konts["pieredze"],
      registret_konts["speles"]
    ])
  return redirect("/")

@app.route('/visi_konti')
def visi_lietotaji():
  rezultats = select_sql("SELECT * FROM Konts")
  return render_template("visi_konti.html", rezultats = rezultats)

@app.route("/konts_pieslegties", methods=["POST", "GET"])
def konts_pieslegties():
  pieslegties_konts = {}
  lietotajvards_result = None 
  parole_result = None 
  if request.method == "POST":
    pieslegties_konts["lietotajvards"] = request.form["lietotajvards"]
    pieslegties_konts["parole"] = request.form["parole"]
    lietotajvards_result = select_sql("SELECT lietotajvards FROM Konts WHERE lietotajvards = ?", (pieslegties_konts["lietotajvards"],))
    parole_result = select_sql("SELECT parole FROM Konts WHERE parole = ?", (pieslegties_konts["parole"],))
    if lietotajvards_result and parole_result: 
      select_sql("DROP TABLE IF EXISTS Session")
      select_sql("CREATE TABLE IF NOT EXISTS Session (\
      konts_ID INTEGER PRIMARY KEY AUTOINCREMENT, \
      lietotajvards TEXT, \
      parole TEXT, \
      limenis INT, \
      pieredze INT, \
      dziviba INT, \
      speles INT)")
      insert_sql("INSERT INTO Session (lietotajvards, parole, pieredze, dziviba, speles) VALUES (?, ?, ?, ?, ?)" ,[
        pieslegties_konts["lietotajvards"],
        pieslegties_konts["parole"],
        0,
        100,
        0
      ])
      return redirect("/sakt_speli")
    else:
      return render_template("pieslegties_konts.html")

  else:
    return render_template("pieslegties_konts.html")

@app.route("/sakt_speli", methods=["POST", "GET"])
def sakt_speli():
  session = select_sql("SELECT * FROM Session")
  rezultats = select_sql("SELECT lietotajvards, limenis, pieredze FROM Konts WHERE lietotajvards = ?", (session[0][1],))
  current_experience = rezultats[0][2]
  level = None
  if current_experience <= 100:
    level = 1
  if current_experience >= 100:
    level = 2
  if current_experience >= 250:
    level = 3
  if current_experience >= 500:
    level = 4
  if current_experience >= 1000:
    level = 5
  if current_experience >= 2000:
    level = 6
  if current_experience >= 4000:
    level = 7
  if current_experience >= 8000:
    level = 8
  if current_experience >= 10000:
    level= 9
  if current_experience >= 15000:
    level = 10

  xp = rezultats[0][1]

  if level == 1:
    xp = 100 - current_experience
  if level == 2:
    xp = 250 - current_experience
  if level == 3:
    xp = 500 - current_experience
  if level == 4:
    xp = 1000 - current_experience
  if level == 5:
    xp = 2000 - current_experience
  if level == 6:
    xp = 4000 - current_experience
  if level == 7:
    xp = 6000 - current_experience
  if level == 8:
    xp = 10000
  if level == 9:
    xp = 14000
  if level == 10:
    xp = 20000

  insert_sql("UPDATE Konts SET limenis = ? WHERE lietotajvards = ?", (level, session[0][1]))

  return render_template("sakt_speli.html", rezultats = rezultats, xp = xp, level = level)

@app.route("/izvele")
def spele_izvele():
  session = select_sql("SELECT * FROM Session")
  rezultats = select_sql("SELECT lietotajvards, limenis, pieredze FROM Konts WHERE lietotajvards = ?", (session[0][1],))
  insert_sql("UPDATE Session SET dziviba = ? WHERE lietotajvards = ?" , (100, session[0][1]))
  insert_sql("UPDATE Session SET pieredze = ? WHERE lietotajvards = ?", (0, session[0][1]))
  xp = rezultats[0][2]
  return render_template("izvele.html", xp = xp)

@app.route("/spele_kauja")
def spele_kauja():
  session = select_sql("SELECT * FROM Session")
  rezultats = select_sql("SELECT lietotajvards, limenis, pieredze FROM Konts WHERE lietotajvards = ?", (session[0][1],))
  hp = session[0][5]
  xp = session[0][4]
  xp_ieguts = (random.randrange(10, 30))
  xp += xp_ieguts
  hp_zaudets = (random.randrange(12, 26))
  hp -= hp_zaudets

  if hp <= 0:
    return redirect("tu_zaudeji")
  insert_sql("UPDATE Session SET dziviba = ? WHERE konts_ID = ?", (hp, session[0][0]))
  insert_sql("UPDATE Session SET pieredze = ? WHERE konts_ID = ?", (xp, session[0][0]))
  return render_template("kauja.html", xp_ieguts = xp_ieguts, hp_zaudets = hp_zaudets, xp = xp, hp = hp)

@app.route("/beigas")
def beigas():
  session = select_sql("SELECT * FROM Session")
  rezultats = select_sql("SELECT lietotajvards, limenis, pieredze, speles FROM Konts WHERE lietotajvards = ?", (session[0][1],))
  xp_konts = rezultats[0][2]
  xp = session[0][4]
  xp_konts = xp_konts + xp
  insert_sql("UPDATE Konts SET pieredze = ? WHERE lietotajvards = ?", (xp_konts, session[0][1]))
  insert_sql("UPDATE Konts SET speles = ? WHERE lietotajvards = ?", (rezultats[0][3] + 1, session[0][1]))
  return render_template("beigas.html", xp = xp, xp_konts = xp_konts)

@app.route("/tu_zaudeji")
def tu_zaudeji():
  session = select_sql("SELECT * FROM Session")
  rezultats = select_sql("SELECT lietotajvards, limenis, pieredze, speles FROM Konts WHERE lietotajvards = ?", (session[0][1],))
  xp_konts = rezultats[0][2]
  xp = session[0][4]
  xp_konts = xp_konts + xp
  insert_sql("UPDATE Konts SET pieredze = ? WHERE lietotajvards = ?", (xp_konts, session[0][1]))
  insert_sql("UPDATE Konts SET speles = ? WHERE lietotajvards = ?", (rezultats[0][3] + 1, session[0][1]))
  return render_template("tu_zaudeji.html", xp = xp, xp_konts = xp_konts)

@app.route("/ranga_tabula")
def ranga_tabula():
  sakartot = select_sql("SELECT lietotajvards, limenis, pieredze, speles FROM Konts ORDER BY speles DESC")
  return render_template("ranga_tabula.html", sakartot = sakartot)

if __name__ =="__main__":
   app.run(host = '0.0.0.0',port = 8080)