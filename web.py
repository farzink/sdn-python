from flask import Flask, url_for, jsonify
from flask import render_template, request
import network
import db

app = Flask(__name__)

second_layer_flag = False

def hello():
    return "Hello World!"


@app.route("/")
def index():
    return render_template('/index.html', name="")


@app.route("/network")
def getNetwork():    
    network.createTopology()
    #buildGraph()
    #getShortestPathFor("2.1", "2.2")
    
    db.prepareConnection()    
    network.buildGraphByTable()
    count = 1
    result = []
    for path in network.getShortestPathFor("2.1", "2.3"):
        result.append({ 'id': count, 'path': path})
        count+=1
    return jsonify(result)





# @app.route("/shortestpath", methods=['GET'])
# def shortestPath():
#     return jsonify({ "first": request.args["source"], "second": request.args["destination"]})


@app.route("/networkgraph")
def getPath():
    return jsonify([{'id': '1'}, {'id': '2'}])


@app.route("/shortestpath", methods=['POST'])
def shortestPath():
    data = request.data.replace("{", "").replace("}", "").split(",");    
    src = data[0].replace("'", "").replace('"', "").split(":")[1];
    des = data[1].replace("'", "").replace('"', "").split(":")[1];
    print(src)
    print(des)
    network.createTopology()
    network.buildGraph()
    
    if second_layer_flag:
        network.applyLayerTwoLinks()    
    
    paths=[]
    for path in network.getShortestPathFor(src, des):
         print(path)
         paths.append({ "path": path } )
    return jsonify([{ "paths": paths}])
    

@app.route("/applayertwo", methods=['GET'])
def ApplyLayerTwo():
    global second_layer_flag
    second_layer_flag = not second_layer_flag
    return jsonify([{ "result": second_layer_flag}])
    









@app.route("/map")
def networkMap():
    global second_layer_flag
    network.reset()
    network.createTopology()
    network.buildGraph()
    if second_layer_flag:
        network.applyLayerTwoLinks()    
    return jsonify([
            {
                "nodes": network.getHosts(),
                "switches": network.getSwitches(),
                "edges": network.getEdges()          
            }
        ])
    
