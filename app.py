import os
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for
import networkx as nx
import plotly.graph_objs as go

app = Flask(__name__)

# base directory for saving the data
basedir = os.path.abspath(os.path.dirname(__file__))

#allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx'}

def allowed_file(filename):
    '''
    check file extension
    :param filename: name of the file (str)
    :return: filename validity (boolean)
    (source: https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/)
    '''

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_graph(path, names):
    '''
    generate a networkx graph
    :param path: the path to the data
    :param names: column names in data
    :return: a networkx graph object
    '''

    # extract node and edge information from xlsx file
    xls = pd.ExcelFile(path)
    edges = pd.read_excel(xls, 'edges', usecols=range(0, 3))
    nodes = pd.read_excel(xls, 'nodes', usecols=range(0, 3))

    # create the graph from the edge list as directed graph
    graph = nx.from_pandas_edgelist(edges, source=names["source"], target=names["target"], edge_attr=names["weight"],
                                    create_using=nx.DiGraph)

    # extract node labels
    node_lab = dict(zip(nodes[names["id"]], nodes[names["label"]]))

    # relabel graph with labels
    graph = nx.relabel_nodes(graph, node_lab)

    # extract node colors
    node_col = dict(zip(nodes[names["id"]], nodes[names["color"]]))

    return graph, node_col, node_lab


def generate_coordinates(pos, graph):
    '''
     extract coordinates for given layout and graph
     :param pos: the layout (given as a networkx layout)
     :param graph: the networkx graph object
     :return: x, y and z coordinates for the nodes and for the edges
     (could be optimized by only giving back node coordinates and a adjacency matrix)
     '''


    x_nodes = []
    y_nodes = []
    z_nodes = []

    x_edges = []
    y_edges = []
    z_edges = []

    len_pos = len(list(pos.values())[0])
    if len_pos is 2:
        # go through nodes
        for node in graph.nodes:
            x_nodes.append(pos[node][0])
            y_nodes.append(pos[node][1])

        # go through edges
        for edge in graph.edges:
            x_edges.append([pos[edge[0]][0], pos[edge[1]][0], None])
            y_edges.append([pos[edge[0]][1], pos[edge[1]][1], None])

        z_nodes = None
        z_edges = None

    elif len_pos is 3:
        # go through nodes
        for node in graph.nodes:
            x_nodes.append(pos[node][0])
            y_nodes.append(pos[node][1])
            z_nodes.append(pos[node][2])

        # go through edges
        for edge in graph.edges:
            x_edges.append([pos[edge[0]][0], pos[edge[1]][0], None])
            y_edges.append([pos[edge[0]][1], pos[edge[1]][1], None])
            z_edges.append([pos[edge[0]][2], pos[edge[1]][2], None])

    else:
        return None

    return x_nodes, y_nodes, z_nodes, x_edges, y_edges, z_edges

def get_node_text(graph, names,  include_incoming = True, include_outgoing = True):
    '''
    create the hover text for the nodes
    :param graph: the networkx graph object
    :param names: column names in data (dict)
    :param include_incoming: include incoming edges in the text (boolean)
    :param include_outgoing: include outgoing edges in the text (boolean)
    :return: list of strings containing the text for each node
    '''

    node_info = {}
    # go through all the nodes an extract the necessary information
    for node in graph.nodes:
        elements = list(graph.in_edges(node, data=True))
        store = "Node name: <b>" + str(node) + "</b>"
        # save names from incoming edges
        if include_incoming:
            store += "<br><br>Incoming edges:"
            if len(elements) is not 0:
                for element in elements:
                    store += "<br><b>" + element[0] + "</b> - weight: " + str(element[2].get(names["weight"]))
            # if there is none, write "none"
            else:
                store += "<br>None"
            elements = list(graph.out_edges(node, data=True))
        # save names from outgoing edges
        if include_outgoing:
            store += "<br><br>Outgoing edges:"
            if len(elements) is not 0:
                for element in elements:
                    store += "<br><b>" + element[1] + "</b> - weight: " + str(element[2].get(names["weight"]))
            # if there is none, write "none"
            else:
                store += "<br>None"
        node_info[node] = store

    return list(node_info.values())


def get_figure(graph, dim, node_col, node_info, names):
    '''
    create the network plot with plotly
    :param graph: the networkx graph object
    :param dim: the plot dimension (2d or 3d)
    :param node_col: a dictionary with the node colors (names as keys)
    :param node_info: list of strings with the node info
    :param names: column names in data (dict)
    :return: a plotly figure containing all the necessary information for plotting
    '''

    trace = []
    weights = list(nx.get_edge_attributes(graph, names["weight"]).values())
    x_node, y_node, z_node, x_edge, y_edge, z_edge = generate_coordinates(nx.circular_layout(graph, dim=dim), graph)

    if dim is 2:

        for i in range(0, len(x_edge)):
            trace.append(go.Scatter(x=x_edge[i],
                                    y=y_edge[i],
                                    mode='lines', hoverinfo='none', opacity=0.5,
                                    line=dict(color='black', width=weights[i])))

        trace.append(go.Scatter(x=x_node, y=y_node, mode='markers',
                                marker=dict(symbol='circle', size=15, color=list(node_col.values()),
                                            line=dict(color='rgb(50,50,50)', width=0.5)), text=node_info,
                                hoverinfo='text'))

        axis = dict(showline=False, zeroline=False, showgrid=False, showticklabels=False, title='')

        return(go.Figure(
            data=trace,
            layout=go.Layout(
                title="RAAN-Network 2D",
                width=1000,
                height=1000,
                showlegend=False,
                xaxis=dict(axis),
                yaxis=dict(axis),
                plot_bgcolor='rgba(0,0,0,0)',
                annotations=[
                    dict(ax=x_edge[i][0], ay=y_edge[i][0], axref='x', ayref='y',
                         x=x_edge[i][1], y=y_edge[i][1], xref='x', yref='y',
                         showarrow=True, arrowhead=3, arrowsize=2, width=1, opacity=0.5) for i in range(0, len(x_edge))
                ]

            )
        ))


    elif dim is 3:

        for i in range(0, len(x_node)):
            trace.append(go.Scatter3d(x=x_edge[i],
                                      y=y_edge[i],
                                      z=z_edge[i],
                                      mode='lines', hoverinfo='none', opacity=0.5,
                                      line=dict(color='black', width=weights[i])))

        trace.append(go.Scatter3d(x=x_node, y=y_node, z=z_node, mode='markers',
                                  marker=dict(symbol='circle', size=15,
                                              color=list(node_col.values()),
                                              line=dict(color='rgb(50,50,50)', width=0.5)),
                                  text=node_info, hoverinfo='text'))

        axis = dict(showbackground=False, showline=False, zeroline=False, showgrid=False, showticklabels=False,
                    title='')

        return(go.Figure(
            data=trace,
            layout=go.Layout(
                title="RAAN-Network 3D",
                width=1000,
                height=1000,
                showlegend=False,
                scene=dict(
                    xaxis=dict(axis),
                    yaxis=dict(axis),
                    zaxis=dict(axis),
                )
            )
        ))

    else:
        return None


@app.route("/")
def index():
        return render_template('index.html')


@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    '''
    process uploaded data
    '''

    if request.method == "POST":
        if request.files:

            file = request.files["file"]
            filename = file.filename

            if allowed_file(filename):

                file.save(os.path.join(basedir+"/uploads/", file.filename))
                path = os.path.join(basedir+"/uploads/", file.filename)

                return redirect(url_for('network_plot', path = path))

            else:
                return "Invalid file type"

@app.route('/network_plot')
def network_plot():
    '''
    create a network plot
    :return: a plotly figure
    '''

    names = {"id": "node_id", "label": "node_label", "color": "node_color", "source": "source_id", "target": "target_id", "weight": "weights"}

    #create the graph, produce the 2d and 3d plots
    graph, node_col, node_lab = generate_graph(request.args.get('path', None), names)
    fig2d = get_figure(graph, 2, node_col, get_node_text(graph, names), names)
    fig3d = get_figure(graph, 3, node_col, get_node_text(graph, names), names)

    # write both 2d and 3d plot to a html file, return the html file
    with open(basedir + '/templates/graphs.html', "w") as f:
        f.write(fig2d.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig3d.to_html(full_html=False, include_plotlyjs='cdn'))

    return render_template('graphs.html')


if __name__ == '__main__':
    app.run(debug=True)