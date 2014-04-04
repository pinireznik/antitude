/* global d3 */
/* global autobahn */
/* global $ */
(function() {
    "use strict";
    /* TODO:
     * Fix the goddam ID/IP/Name issue.
     *  - keep up with messages
     *    - cljs?
     *  - be nice to separate base Serf functionality
     */
    var w = 960,
        h = 500;

    var midx = Math.floor(w/2),
        midy = Math.floor(h/2);

    var g_nodes = [];

    var force = d3.layout.force()
        .gravity(0)
        .charge(0)
        .linkDistance(50)
        .nodes(g_nodes)
        .size([w, h]);

    var links = force.links();
    var pendingLinks = [];
    var started = false;
    var colors = { "alive": "#5cb85c", 
                   "failed": "#d9534f",
                   "fixing": "#f0ad4e",
                   "fixed": "#5cb85c",
                   "leaving": "gray"};


    force.start();

    var svg = d3.select("#node_graph").append("svg:svg")
        .attr("width", w)
        .attr("height", h);

    //Definition of graphic for arrows on deps
    svg.append("svg:defs").append("svg:marker")
        .attr("id", "triangle")
        .attr("refX", "14")
        .attr("refY", "6.5") 
        .attr("markerUnits", "strokeWidth")
        .attr("markerWidth", "26")
        .attr("markerHeight", "26")
        .attr("orient", "auto")
        .append("svg:path")
          .attr("d", "M2,4 L2,9 L5,6.5 L2,4")
          .attr("style", "fill: #000000;");

    svg.append("svg:rect")
        .attr("width", w)
        .attr("height", h);

    force.on("tick", function(e) {
        var q = d3.geom.quadtree(g_nodes),
            k = e.alpha * 0.1,
            i = 0,
            n = g_nodes.length,
            o;

        for (i=0; i<n; i++) {
            o = g_nodes[i];
            if (o.fixed) {
                continue;
            }
            //Move towards middle
            o.x += (midx - o.x) * k;
            o.y += (midy - o.y) * k;
            q.visit(collide(o));
        }

        svg.selectAll(".node")
            .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")";});

        svg.selectAll("circle")
           .attr("r", function(n) { return n.radius - 2; }) // -2 creates border
           .style("fill", function(n) {return colors[n.status];});

        svg.selectAll("text")
            .text(function(d) { return d.role.substring(0,1); });

        var lines = svg.selectAll(".link");
        lines.data(links).enter()
            .insert("line", ".node")
            .attr("class", "link")
            .attr("marker-end", "url(#triangle)");
        lines.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
    });

    function collide(node) {
        var r = node.radius + 16,
            nx1 = node.x - r,
            nx2 = node.x + r,
            ny1 = node.y - r,
            ny2 = node.y + r;

        return function(quad, x1, y1, x2, y2) {
            if (quad.point && (quad.point !== node)) {
                var x = node.x - quad.point.x,
                    y = node.y - quad.point.y,
                    l = Math.sqrt(x * x + y * y),
                    r = node.radius + quad.point.radius;
                if (l < r) {
                    l = (l - r) / l * 0.5;
                    node.px += x * l;
                    node.py += y * l;
                }
            }
            return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
        };
    }

    var connection = new autobahn.Connection({
        url: 'ws://' + window.location.host  + '/ws',
        realm: 'realm1'
    });

    var nodes = {};

    function logMessage(message) {

        console.log(message);

        for (var key in message) {
            //Make sure avoid anything in prototype
            if (message.hasOwnProperty(key)) {
                $("#message_log").append("<p>" + key + " " + message[key] + "</p>");
            }
        }
        while ($("#message_log p").length > 5) {
            $("#message_log p")[0].remove();
        }

    }

    function updateNodes(error, json) {

        if (error) {
            return console.warn(error);
        }

        //F'ng hack to fix multiple IPs dead/alive.
        //We should never have used IP as ID. I told the mofos! ;)
        var seenIPs = [];
        for (var i = 0; i < json.members.length; i++) {
            var m = json.members[i];

            if (m.status == "left" && seenIPs.indexOf(m.addr) != -1) { 
                continue;
            }
            seenIPs.push(m.addr);

            var id = "A" + m.addr.split(":")[0].replace(/\./g, "d");
            var add = false;
            if (!(id in nodes)) {
                //Set a default value for memory
                nodes[id] = {"memory": 20};
                nodes[id].par = "None";
                add = true;
            }
            nodes[id].addr = m.addr;
            nodes[id].radius = 8 + nodes[id].memory / 2;
            nodes[id].name = m.name; 
            nodes[id].status = m.status;
            nodes[id].id = "A" + m.addr.split(":")[0].replace(/\./g, "d");
            if (m.tags.role) {
                nodes[id].role = m.tags.role;
            } else {
                nodes[id].role = "?";
            }

            if (m.tags.parent) {
                if (nodes[id].par !== m.tags.parent) {
                    nodes[id].par = m.tags.parent;
                    var toAdd = nodes[id].par.split(",");
                    for (var j=0; j< toAdd.length; j++) {
                        pendingLinks.push({sourceId: addrToId(toAdd[j]), targetId: id});
                    }
                }
            }

            if (add) {
                addGraphNode(nodes[id]);
            }

            if (nodes[id].status === "left") {
                removeGraphNode(nodes[id]);
            }
        }
        //Should also delete any nodes that don't appear in list

        checkPendingLinks();
        updateMemberTable();
        updateGraph();
    }

    function checkPendingLinks() {

        for (var i = pendingLinks.length -1; i >= 0; i--) {

            var src = nodes[pendingLinks[i].sourceId];
            var trg = nodes[pendingLinks[i].targetId];

            //think src && trg should work
            if (typeof(src) != "undefined" && typeof(trg) != "undefined") {
                //console.log(src);
                //console.log(trg);
                links.push({source: src, target: trg});
                pendingLinks.splice(i, 1);
            }

        }

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
                tr.append("td").text(n.role);
                tr.append("td").text(n.par);
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
        thead.append("th").text("Role");
        thead.append("th").text("Parent");
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

    function removeGraphNode(n) {
        var ind = g_nodes.indexOf(n);
        if (ind !== -1) {
            g_nodes.splice(ind, 1);
        }
        d3.select("#" + n.id).remove();

    }

    function addGraphNode(n) {

        n.x = Math.floor(Math.random() * w);
        n.y = Math.floor(Math.random() * w);

        var g = svg.append("svg:g")
            .data([n])
            .attr("id", n.id)
            .attr("class", "node")
            .attr("transform", function (n) { return "translate(" + n.x + "," + n.y + ")";});
        var circ = g.append("svg:circle")
            .data([n])
            .attr("r", function(n) { return n.radius - 2; }) // -2 creates border
            .style("fill", function(n) {return colors[n.status];});
        circ.append("svg:title")
            .text(function(d) { return d.addr; });
        g.append("text")
            .data([n])
            .attr("dy", ".3em")
            .style("text-anchor", "middle")
            .text(function(d) { return d.role.substring(0,1); });

        g_nodes.push(n);

    }

    function updateGraph() {

        force.start();

    }

    function addrToId(addr) {
        return "A" + addr.replace(/\./g, "d").replace(/\n/g, "");
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

            /*
             * Ignore NEWNODE and use member-join
             * Read member-update
             * Figure out leave stuff */
            for (var key in message) {
                if (message.hasOwnProperty(key)) {
                    console.log("got key " + key);
                    if (key === "FIXING") {
                        var target = addrToId(message[key]);
                        nodes[target].status = "fixing";
                        updateMemberTable();
                        updateGraph();
                    } else if (key === "FIXED") {
                        var target = addrToId(message[key]);
                        nodes[target].status = "fixed";
                        updateMemberTable();
                        updateGraph();
                    } else if (key === "REMOVENODE") {
                        setTimeout(updateNodesFunc, 500);
                    } else if (key === "MEMORY_LEVEL") {
                        var level = extractArg("LEVEL", message[key]);
                        var target = extractArg("IP", message[key]);

                        if (level !== "" && target !== "") {
                            var ilevel = +level;
                            if (ilevel !== nodes[addrToId(target)].memory) {
                                nodes[addrToId(target)].memory = ilevel;
                                nodes[addrToId(target)].radius = 8 + ilevel/2;
                                updateMemberTable();
                                updateGraph();
                            }
                        }
                    } else if (key === "member-join" || key === 'member-update' || key === 'member-leave') {
                        updateNodesFunc();
                    }
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

})();
