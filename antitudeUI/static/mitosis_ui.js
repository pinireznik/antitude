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
        h = 800;

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
    var ipRole = {};

    var roleColors = {
        "ui": "#5c58cc",
        "database": "#660066",
        "loadbalancer": "#f0ad4e"
    };
    // TODO: not the same colors!
    var statusColors = {
        "alive": "#5cb85c",
        "failed": "#d9534f",
        "fixing": "#f0ad4e",
        "fixed": "#5cb85c",
        "leaving": "gray"
    };
    var strokeWidth = 7;
    var IP_BASE = "10.99.176.";

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

    // replaced by legend
    /*
    svg.append("svg:rect")
        .attr("width", w)
        .attr("height", h);
    */

    force.on("tick", function(e) {
        var q = d3.geom.quadtree(g_nodes),
            // 0.1
            k = e.alpha * 0.03,
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

        // TODO: DRY

        svg.selectAll(".node")
            .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")";});

        svg.selectAll("circle")
           .attr("r", function(n) { return n.radius - 2; }) // -2 creates border
           .style("fill", function(n) {return n.color;})
           .style("stroke", function(n) {return n.stroke;})
           .style("stroke-width", strokeWidth);

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
        var i, id;

        if (error) {
            return console.warn(error);
        }

        //F'ng hack to fix multiple IPs dead/alive.
        //We should never have used IP as ID. I told the mofos! ;)
        var seenIPs = [], seenIDs = {};
        for (i = 0; i < json.members.length; i++) {
            var m = json.members[i];

            if (m.status == "left" && seenIPs.indexOf(m.addr) != -1) { 
                continue;
            }
            seenIPs.push(m.addr);

            id = "A" + m.addr.split(":")[0].replace(/\./g, "d");
            seenIDs[id] = i;
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
                //console.log('id:' + id + ', role: ' + m.tags.role);
                nodes[id].role = m.tags.role;
                nodes[id].color = roleColors[m.tags.role];
                nodes[id].stroke = statusColors[m.status];
            } else {
                nodes[id].role = "?";
                nodes[id].color = "grey";
                nodes[id].stroke = "black";
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

        // delete any nodes that don't appear in list
        var mykeys = Object.keys(nodes);
        var killedNodes = {};
        for(i = 0; i < mykeys.length; i++) {
            if(!(mykeys[i] in seenIDs)) {
                removeGraphNode(nodes[mykeys[i]]);
                killedNodes[nodes[mykeys[i]].id] = 0; // use this as hash
            }
        }

        checkPendingLinks(killedNodes);
        updateMemberTable();
        updateGraph();
    }

    function checkPendingLinks(killedNodes) {
        var i;
        for (i = pendingLinks.length -1; i >= 0; i--) {

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

        // delete any dangling links TODO: not working
        for(i = 0; i < links.length; i++) {
            if(links[i].source.id in killedNodes || links[i].target.id in killedNodes)
                links.splice(i, 1);
        }
    }

    // TODO: quick hack to enable scaling down
    function cleanLinks() {
        //links = force.links(); // swipe links
        links.splice(0,links.length);
        svg.selectAll(".link").remove();
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
        //thead.append("th").text("Memory");
        thead.append("th").text("Load");
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

    // TODO: DRY
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
            .style("fill", function(n) {return n.color;})
            .style("stroke", function(n) {return n.stroke;})
            .style("stroke-width", strokeWidth);
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
/*
    // new stuff
    {
		d3.json("data.json", function(error, json) {
		    if (error)
                return console.warn(error);
			for(var i = 0; i < json.length; i++) {
				onevent1(json[i]);
			}
		});
	}
    // end new stuff
  */
	var updateNodesFunc = function() {
		//d3.json("members", updateNodes);
        rearrange();
	};
    function onevent1(args) {
            //var message = $.parseJSON(args);
			var message = args;
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
                                nodes[addrToId(target)].status = n.status;
                                updateMemberTable();
                                updateGraph();
                            }
                        }
                    } else if (key === "member-join" || key === 'member-update' || key === 'member-leave') {
                        updateNodesFunc();
                    }
                }
            }


        }

    //setTimeout(rearrange, 1000);

    function roleDice() {
        var roles = ["ui", "database", "loadbalancer"];
        var roleP = [0.33,  0.33, 0.33];
        var totalP = 0.0, curP = 0.0, num = Math.random();
        var i;

        for(i = 0; i < roles.length; i++)
            totalP += roleP[i];

        for(i = 0; i < roles.length; i++) {
            curP += roleP[i] / totalP;
            if(num < curP)
                return roles[i];
        }
        return roles[roles.length - 1];
    }

    function genName() {
        var hex = "0123456789abcdef";
        var name = "";
        for(var i = 0; i < 12; i++)
            name += hex[Math.floor(Math.random()*hex.length)];
        return name;
    }

    // generate random memory usage
    function genMemory() {
        //return Math.floor(Math.random() * 100);

        return 20 + Math.floor(Math.random() * 50);
    }

    function getNodeCount() {
        return 50;
    }

    // generate some random parents
    function genParent() {
        var parent = IP_BASE + Math.floor(Math.random() * getNodeCount());
        /*var pparent = 0.5 / getNodeCount();
        for(var i = 0; i < getNodeCount(); i++) {
            parent += "," + IP_BASE + (i + 1);
        }*/
        return parent;
    }

    // make the graph
    function rearrange() {
        var nodeList = [{"role": "database", "memory": 20}, {"role": "ui", "memory": 20, "parent": 0}];
        myupdate(nodeList);
    }

    function heal() {
        var id = failedNodes.shift();
        nodes[id].status = "alive";
    }

    var ANIM_DELAY = 300;
    var failedNodes = [];
    function animate(animation, i, len, dbg_frame, dbg_i) {
        if(i == 0) {
            //console.log("animate() START " + dbg_frame + " " + dbg_i);
        }
        if(animation.type == "blow") {
            var mynodes = [animation.node];
            if(typeof(animation.node) == "undefined")
                mynodes = animation.nodes;
            var id, j;
            for(j = 0; j < mynodes.length; j++) {
                id = addrToId(IP_BASE + (mynodes[j] + 1));

                // blinking (fails)
                if(Math.random() < 0.5) {
                    nodes[id].status = "failed";
                    failedNodes.push(id);
                    setTimeout(heal, 1000);
                }
                // end blinking

                if(nodes[id].status != "failed") {
                    nodes[id].memory = Math.floor(animation.from + i * (animation.to - animation.from) / len);
                    //nodes[id].memory = Math.floor(animation.to);
                    // jumping not probelm here (not only)
                    if(i == len - 1)
                        nodes[id].memory += Math.floor(Math.random() * 20) - 10;
                }
            }
            //console.log("ANIM id: " + (IP_BASE + (animation.node + 1)) + ", memory: " + nodes[id].memory);
        }
        updateNodes(false, membersJson);
        if(++i < len)
            setTimeout(function() {animate(animation, i, len, dbg_frame, dbg_i)}, ANIM_DELAY);
        //else
            //console.log("animate() END " + dbg_frame + " " + dbg_i);
    }

    var movieDef = [
        {
            "nodes": [
                {"role": "ui", "memory": 20}
            ],
            "animation": [],
            "timeout": 2000
        },
        {
            "nodes": [
                {"role": "database", "memory": 20},
                {"role": "ui", "memory": 20, "parent": 0}
            ],
            "animation": [
                {"type": "blow", "node": 1, "from": 20, "to": 80}
            ],
            "timeout": 3000,
            "add_timeout": 2000
        },
        {
            "nodes": [
                {"role": "database", "memory": 20},
                {"role": "ui", "memory": 30, "parent": 0},
                {"role": "loadbalancer", "memory": 20},
                {"role": "ui", "memory": 30, "parent": 0}
            ],
            "animation": [
                {"type": "blow", "node": 0, "from": 20, "to": 30},
                {"type": "blow", "node": 1, "from": 30, "to": 80},
                {"type": "blow", "node": 3, "from": 30, "to": 80}
            ],
            "timeout": 5000,
            "add_timeout": 1000
        },
        {
            "nodes": [
                {"role": "database", "memory": 30},
                {"role": "ui", "memory": 30, "parent": 0},
                {"role": "loadbalancer", "memory": 20},
                {"role": "ui", "memory": 30, "parent": 0},
                {"role": "ui", "memory": 30, "parent": 0},
                {"role": "ui", "memory": 30, "parent": 0},
                {"role": "ui", "memory": 30, "parent": 0}
            ],
            "animation": [
                {"type": "blow", "node": 0, "from": 30, "to": 80},
                {"type": "blow", "node": 2, "from": 20, "to": 50},
                {"type": "blow", "nodes": [1, 3, 4, 5, 6], "from": 30, "to": 60}
            ],
            "timeout": 5000,
            "add_timeout": 1000
        },
        { // trouble here?
            "nodes": [
                {"role": "database", "memory": 30},
                {"role": "ui", "memory": 30, "parent": 0},
                {"role": "loadbalancer", "memory": 20},
                {"role": "ui", "memory": 30, "parent": 0},
                {"role": "ui", "memory": 30, "parent": 0},
                {"role": "ui", "memory": 30, "parent": 0},
                {"role": "ui", "memory": 30, "parent": 7},
                {"role": "database", "memory": 30},
                {"role": "database", "memory": 30},
                {"role": "ui", "memory": 30, "parent": 7},
                {"role": "ui", "memory": 30, "parent": 8},
                {"role": "ui", "memory": 30, "parent": 8},
                {"role": "ui", "memory": 30, "parent": 8}
            ],
            "animation": [
                {"type": "blow", "node": 0, "from": 30, "to": 80},
                {"type": "blow", "node": 2, "from": 20, "to": 40},
                {"type": "blow", "node": 3, "from": 20, "to": 50},
                {"type": "blow", "nodes": [1, 3, 4, 5, 6], "from": 30, "to": 60},
                {"type": "blow", "nodes": [7, 8], "from": 30, "to": 50},
                {"type": "blow", "nodes": [8, 9, 10, 11, 12], "from": 30, "to": 40}
            ],
            //"timeout": 3000
            "timeout": 5000
        },
        // from here, rip apart the existing structure, it won't be visible any more
        {
            "nodes": [
                {"role": "ui", "memory": 21},
                {"role": "ui", "memory": 21},
                {"role": "ui", "memory": 22},
                {"role": "ui", "memory": 23},
                {"role": "ui", "memory": 21},
                {"role": "ui", "memory": 20},
                {"role": "ui", "memory": 22},
                {"role": "ui", "memory": 20},
                {"role": "ui", "memory": 23},
                {"role": "ui", "memory": 24},
                {"role": "ui", "memory": 20},
                {"role": "ui", "memory": 23},
                {"role": "ui", "memory": 23},
                {"role": "ui", "memory": 20},
                {"role": "ui", "memory": 21},
                {"role": "ui", "memory": 23},
                {"role": "ui", "memory": 22},
                {"role": "ui", "memory": 22},
                {"role": "ui", "memory": 21},
                {"role": "ui", "memory": 24},
                {"role": "loadbalancer", "memory": 24},
                {"role": "loadbalancer", "memory": 24},
                {"role": "loadbalancer", "memory": 20},
                {"role": "database", "memory": 20},
                {"role": "database", "memory": 24},
                {"role": "database", "memory": 21},
                {"role": "database", "memory": 23},
                {"role": "database", "memory": 24},
                {"role": "database", "memory": 21}
            ],
            "animation": [
                {"type": "blow", "nodes": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "from": 20, "to": 40},
                {"type": "blow", "nodes": [20, 21, 22], "from": 20, "to": 40},
                {"type": "blow", "nodes": [23, 24, 25, 26, 27, 28], "from": 20, "to": 40}
            ],
            "timeout": 5000,
            "animation_delay": 1000
        },
        // scaling down again, reverse order
        {
            "nodes": [
                {"role": "database", "memory": 80},
                {"role": "ui", "memory": 60, "parent": 0},
                {"role": "loadbalancer", "memory": 40},
                {"role": "ui", "memory": 60, "parent": 0},
                {"role": "ui", "memory": 60, "parent": 0},
                {"role": "ui", "memory": 60, "parent": 0},
                {"role": "ui", "memory": 60, "parent": 7},
                {"role": "database", "memory": 50},
                {"role": "database", "memory": 50},
                {"role": "ui", "memory": 40, "parent": 7},
                {"role": "ui", "memory": 40, "parent": 8},
                {"role": "ui", "memory": 40, "parent": 8},
                {"role": "ui", "memory": 40, "parent": 8}
            ],
            "animation": [
                {"type": "blow", "node": 0, "from": 80, "to": 30},
                {"type": "blow", "node": 2, "from": 40, "to": 20},
                {"type": "blow", "node": 3, "from": 50, "to": 20},
                {"type": "blow", "nodes": [1, 3, 4, 5, 6], "from": 60, "to": 30},
                {"type": "blow", "nodes": [7, 8], "from": 50, "to": 30},
                {"type": "blow", "nodes": [8, 9, 10, 11, 12], "from": 40, "to": 30}
            ],
            "timeout": 5000,
            "secret_sauce": "cleanLinks"
        },
        {
            "nodes": [
                {"role": "database", "memory": 80},
                {"role": "ui", "memory": 60, "parent": 0},
                {"role": "loadbalancer", "memory": 50},
                {"role": "ui", "memory": 60, "parent": 0},
                {"role": "ui", "memory": 60, "parent": 0},
                {"role": "ui", "memory": 60, "parent": 0},
                {"role": "ui", "memory": 60, "parent": 0}
            ],
            "animation": [
                {"type": "blow", "node": 0, "from": 80, "to": 30},
                {"type": "blow", "node": 2, "from": 50, "to": 20},
                {"type": "blow", "nodes": [1, 3, 4, 5, 6], "from": 60, "to": 30}
            ],
            "timeout": 5000,
            "add_timeout": 1000,
            "secret_sauce": "cleanLinks"
        },
        {
            "nodes": [
                {"role": "database", "memory": 30},
                {"role": "ui", "memory": 80, "parent": 0},
                {"role": "loadbalancer", "memory": 20},
                {"role": "ui", "memory": 80, "parent": 0}
            ],
            "animation": [
                {"type": "blow", "node": 0, "from": 30, "to": 20},
                {"type": "blow", "node": 1, "from": 80, "to": 30},
                {"type": "blow", "node": 3, "from": 80, "to": 30}
            ],
            "timeout": 3000,
            "add_timeout": 1000,
            "secret_sauce": "cleanLinks"
        },
        {
            "nodes": [
                {"role": "database", "memory": 20},
                {"role": "ui", "memory": 80, "parent": 0}
            ],
            "animation": [
                {"type": "blow", "node": 1, "from": 80, "to": 20}
            ],
            "timeout": 2000,
            "add_timeout": 2000,
            "secret_sauce": "cleanLinks"
        }
    ];

    var iframe = 0;
    function movie() {
        console.log("movie(): " + iframe);
        myupdate(movieDef[iframe].nodes);
        if(movieDef[iframe].secret_sauce == "cleanLinks") {
            console.log("secret sauce: cleanLinks");
            cleanLinks();
        }

        if(typeof(movieDef[iframe].animation_delay) == "undefined")
            movieDef[iframe].animation_delay = 100;
        movieDef[iframe].animation_delay = 0; // TODO testing
        setTimeout(function() {
            iframe--;
            console.log("movie(): ANIMATE " + iframe);
            var animation = movieDef[iframe].animation;
            for(var i = 0; i < animation.length; i++) {
                if(typeof(animation[i].add_timeout) == "undefined")
                    animation[i].add_timeout = 0;

                animate(animation[i], 0, (movieDef[iframe].timeout + animation[i].add_timeout) / ANIM_DELAY, iframe, i);
            }
            iframe++;
        }, movieDef[iframe].animation_delay);

        if(++iframe < movieDef.length) {
            console.log("movie(): ANIMATE iframe=" + iframe + " SETTIMEOUT " + movieDef[iframe-1].timeout);
            setTimeout(movie, movieDef[iframe-1].timeout);
        }
    }


    var membersJson;

    function myupdate(nodeList) {
        var memberList = []; // role, [parent], memory

        var addr, tags;
        for(var i = 0; i < nodeList.length; i++) {
            addr = IP_BASE + (i + 1); // TODO pretty?: .0 IP
            //tags = { "role": roleDice() };
            tags = { "role": nodeList[i].role };
            if(typeof(nodeList[i].parent) != "undefined")
                tags["parent"] = IP_BASE + (nodeList[i].parent + 1);
            var statusof = "alive";
            if(nodes[addrToId(addr)] && typeof(nodes[addrToId(addr)].status))
                statusof = nodes[addrToId(addr)].status;
            memberList.push({
                "name": genName(),
                "addr": addr + ":7946",
                "tags": tags,
                "status": statusof
            });
            if(nodes[addrToId(addr)])
                nodes[addrToId(addr)].memory = nodeList[i].memory;
        }

        membersJson = {"members": memberList};
        updateNodes(false, membersJson);
    }

    //rearrange();
    //setTimeout(movie, 500);
    movie();

    //d3.json("members", updateNodes);

})();
