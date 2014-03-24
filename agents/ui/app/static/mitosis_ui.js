/* global d3 */
/* global autobahn */
/* global $ */
(function() {
    "use strict";
    var w = 960,
        h = 500;

    var midx = Math.floor(w/2),
        midy = Math.floor(h/2);


    /*
    var g_nodes = d3.range(5).map(function(i) {
        return {//type: Math.random() * 5 | 0,
                radius: 30,
                fixed:true,
                type:i,
                x: (i+1) * (w / 6),
                y: h / 2
            };
    });
    */
    var g_nodes = [];
    var color = d3.scale.category10();

    var force = d3.layout.force()
        .gravity(0)
        .charge(0)
        .nodes(g_nodes)
        .size([w, h]);

    var colors = { "alive": "green", 
                   "failed": "red",
                   "fixing": "yellow",
                   "fixed": "green"};

    force.start();

    var svg = d3.select("#node_graph").append("svg:svg")
        .attr("width", w)
        .attr("height", h);

    svg.append("svg:rect")
        .attr("width", w)
        .attr("height", h);

    svg.selectAll("circle")
        .data(g_nodes)
        .enter().append("svg:circle")
          .attr("r", function(d) { return d.memory - 2; })
          .style("fill", function(d, i) { return color[d.status]; });

    force.on("tick", function(e) {
        var q = d3.geom.quadtree(g_nodes),
            k = e.alpha * 0.1,
            i = 0,
            n = g_nodes.length,
            o;

        for (i=0; i<g_nodes.length; i++) {
            o = g_nodes[i];
            if (o.fixed) {
                continue;
            }
            //Move towards middle
            o.x += (midx - o.x) * k;
            o.y += (midy - o.y) * k;
            q.visit(collide(o));
        }

        svg.selectAll("circle")
           .attr("cx", function(d) { return d.x; })
           .attr("cy", function(d) { return d.y; })
           .attr("r", function(n) { return n.memory - 2; }) // -2 creates border
           .style("fill", function(n) {return colors[n.status];});
    });

    //var p0;
    /*
    svg.on("mousemove", function() {
        var p1 = d3.mouse(this),
        node = {
            radius:Math.random() * 12 + 4, 
            type: Math.random() * 5 | 0, 
            x: p1[0], 
            y: p1[1], 
            px: (p0 || (p0 = p1))[0], 
            py: p0[1]
        };

        p0 = p1;

        svg.append("svg:circle")
            .data([node])
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; })
            .attr("r", function(d) { return d.radius - 2; })
            .style("fill", function(d) {return color(d.type);})
            .transition()
            .delay(3000)
            .attr("r", 1e-6)
            .each("end", function() { g_nodes.splice(6, 1); })
            .remove();

        g_nodes.push(node);
        force.resume();
    });
    */

    function collide(node) {
        var r = node.memory + 16,
            nx1 = node.x - r,
            nx2 = node.x + r,
            ny1 = node.y - r,
            ny2 = node.y + r;

        return function(quad, x1, y1, x2, y2) {
            if (quad.point && (quad.point !== node)) {
                var x = node.x - quad.point.x,
                    y = node.y - quad.point.y,
                    l = Math.sqrt(x * x + y * y),
                    r = node.memory + quad.point.memory;
                if (l < r) {
                    l = (l - r) / l * 0.5;
                    node.px += x * l;
                    node.py += y * l;
                }
            }
            return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
        };
    }

  /*
  var diameter = 500,
      format = d3.format(",d"),
      color = d3.scale.category20c();


  var bubble = d3.layout.pack()
    .sort(null)
    .size([diameter, diameter])
    .padding(4)
    .value(function (d) { 
        console.log("memory: " + d.memory);
        return d.memory; });

    var colors = { "alive": "green", 
                   "failed": "red",
                   "fixing": "yellow",
                   "fixed": "green"};
                   */
/*
    var svg = d3.select("#node_graph").append("svg")
      .attr("width", diameter)
      .attr("height", diameter)
      .attr("class", "bubble");
*/
    var connection = new autobahn.Connection({
        url: 'ws://127.0.0.1:5000/ws',
        realm: 'realm1'
    });

    var nodes = {};

    function logMessage(message) {

        for (var key in message) {
            //Make sure avoid anything in prototype
            if (message.hasOwnProperty(key)) {
                $("#message_log").append(key + " " + message[key] + "<br/>");
            }
        }

    }

    function updateNodes(error, json) {

        if (error) {
            return console.warn(error);
        }

        for (var i = 0; i < json.members.length; i++) {
            var m = json.members[i];

            var id = "A" + m.addr.split(":")[0].replace(/\./g, "d");
            var add = false;
            if (!(id in nodes)) {
                //Set a default value for memory
                nodes[id] = {"memory": 20};
                add = true;
            }
            nodes[id].addr = m.addr;
            nodes[id].name = m.name; //Yes, I know
            nodes[id].status = m.status;
            nodes[id].id = "A" + m.addr.split(":")[0].replace(/\./g, "d");
            if (add) {
                addGraphNode(nodes[id]);
            }
        }
        //Should also delete any nodes that don't appear in list

        updateMemberTable();
        updateGraph();
    }

    function updateMemberTable() {

        var table = d3.select("#node_table").html("").append("table")
            .attr("class", "table table-bordered table-condensed");
        var tbody = table.append("tbody");

        for (var id in nodes) {
            if (nodes.hasOwnProperty(id)) {
                var n = nodes[id];
                var tr = tbody.append("tr").attr("id", id);
                tr.append("td").text(n.name);
                tr.append("td").text(n.addr);
                tr.append("td").text(n.memory);
                tr.append("td").text(n.status);
                if (n.status === "fixing") {
                    tr.classed("success", false);
                    tr.classed("warning", true);
                } else if (n.status === "fixed") {
                    tr.classed("warning", false);
                    tr.classed("success", true);
                }
            }

        }

        var thead = table.append("thead");
        thead.append("th").text("Name");
        thead.append("th").text("Address");
        thead.append("th").text("Memory");
        thead.append("th").text("Status");

    }

    //Change this to be function on nodes
    function getNodeArray() {

        var children = [];
        for (var id in nodes) {
            if (nodes.hasOwnProperty(id)) {
                children.push(nodes[id]);
            }
        }
        return children;
    }

    function addGraphNode(n) {

        n.x = Math.floor(Math.random() * w);
        n.y = Math.floor(Math.random() * w);

        svg.append("svg:circle")
            .data([n])
            .attr("cx", function(n) { return +n.x; })
            .attr("cy", function(n) { return +n.y; })
            .attr("r", function(n) { return n.memory - 2; }) // -2 creates border
            .style("fill", function(n) {return colors[n.status];})
            .append("svg:title")
            .text(function(d) { return d.addr; })
            .transition();

        g_nodes.push(n);

    }

    function updateGraph() {

        force.start();

        //addGraphNode();

        /*
        var svg = d3.select("#node_graph").html("").append("svg")
            .attr("width", diameter)
            .attr("height", diameter)
            .attr("class", "bubble");

        kids = getNodeArray();
        var node = svg.selectAll(".node")
            .data(bubble.nodes({"children": kids}))
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", function(d) { 
                console.log("in transform"  + d);
                return "translate(" + d.x + "," + d.y + ")"; 
            });

        node.append("title")
            .text(function(d) { return d.addr + ": " + format(d.value); });

        node.append("circle")
            .attr("r", function(d) { return d.r; })
            .style("fill", function(d) { 

                if (d.status in colors) {
                    return colors[d.status];
                } 
                return "white";
            });

        node.append("text")
            .attr("dy", ".3em")
            .style("text-anchor", "middle")
            .text(function(d) { return d.name; });
        bubble.sort();
        */
    }

    function addrToId(addr) {
        return "A" + addr.replace(/\./g, "d");
    }

    function extractArg(arg, string) {

        var re = new RegExp(arg + "=(\\S*)");
        var res = re.exec(string);
        if (res && res.length > 1) {
            return  re.exec(string)[1];
        }
        return "";
    }

    connection.onopen = function (session) {

        var received = 0;

        var updateNodesFunc = function() {
            d3.json("members", updateNodes);
        };
        function onevent1(args) {

            var message = $.parseJSON(args);
            logMessage(message);

            for (var key in message) {
                if (message.hasOwnProperty(key)) {
                    console.log("got key " + key);
                    if (key === "FIXING") {
                        var target = addrToId(message[key]);
                        console.log("got fixing *" + target + "*");
                        nodes[target].status = "fixing";
                        //d3.select("#" + target).classed("success", false);
                        //d3.select("#" + target).classed("warning", true);
                    } else if (key === "FIXED") {
                        var target = addrToId(message[key]);
                        nodes[target].status = "fixed";
                        //d3.select("#" + target).classed("warning", false);
                        //d3.select("#" + target).classed("success", true);
                    } else if (key === "NEWNODE") {
                        setTimeout(updateNodesFunc, 500);
                    } else if (key === "MEMORY_LEVEL") {
                        var level = extractArg("LEVEL", message[key]);
                        var target = extractArg("IP", message[key]);
                        console.log("LEVEL= " + level + " IP= " + target);

                        if (level !== "" && target !== "") {
                            console.log("updating level for " + addrToId(target));
                            nodes[addrToId(target)].memory = +level;
                        }

                    }
                    //Assume always need to do this
                    updateMemberTable();
                    updateGraph();
                }
            }


            received += 1;
            if (received > 5000) {
                console.log("Closing ..");
                connection.close();
            }
        }

        session.subscribe('mitosis.event', onevent1);
    };


    connection.open();


    d3.json("members", updateNodes);

    
    //d3.select(self.frameElement).style("height", diameter + "px");

})();
