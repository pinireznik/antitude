(function() {

    var diameter = 960,
        format = d3.format(",d"),
        color = d3.scale.category20c();

    var bubble = d3.layout.pack()
      .sort(null)
      .size([diameter, diameter])
      .padding(1.5)
      .value(function (d) { return 100; });

    var svg = d3.select("#node_graph").append("svg")
      .attr("width", diameter)
      .attr("height", diameter)
      .attr("class", "bubble");

    var connection = new autobahn.Connection({
        url: 'ws://127.0.0.1:5000/ws',
        realm: 'realm1'}
        );

    var nodes = {};

    function logMessage(message) {

        for (var key in message) {
            $("#message_log").append(key + " " + message[key] + "<br/>");
        }

    }

    function updateNodes(error, json) {

        if (error) {
            return console.warn(error);
        }

        for (var i = 0; i < json.members.length; i++) {
          var m = json.members[i];
          if (!(m.name in nodes)) {
            nodes[m.name] = {"addr": 0};
          }
          nodes[m.name].addr = m.addr;
          nodes[m.name].name = m.name; //Yes, I know
          nodes[m.name].status = m.status;
          nodes[m.name].id = "A" + m.addr.split(":")[0].replace(/\./g, "d");
        }
        //Should also delete any nodes that don't appear in list

        updateMemberTable();
        updateGraph();
    }

    function updateMemberTable() {

        var table = d3.select("#node_table").html("").append("table")
            .attr("class", "table table-bordered table-condensed");
        tbody = table.append("tbody");

        for (var name in nodes) {
            var n = nodes[name];
            var id = "A" + n.addr.split(":")[0].replace(/\./g, "d");
            console.log("id " + id);
            var tr = tbody.append("tr").attr("id", id);
            tr.append("td").text(name);
            tr.append("td").text(n.addr);
            tr.append("td").text(n.status);
        }

        var thead = table.append("thead");
        thead.append("th").text("Name");
        thead.append("th").text("Address");
        thead.append("th").text("Status");

    }

    //Change this to be function on nodes
    function getNodeArray() {

      children = [];
      for (var name in nodes) {
        children.push(nodes[name]);
      }
      return children;
    }

    function updateGraph() {

      kids = getNodeArray();
      var node = svg.selectAll(".node")
        .data(bubble.nodes({children: kids}))
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) { 
          console.log("in transform"  + d);
          return "translate(" + d.x + "," + d.y + ")"; });

      node.append("title")
        .text(function(d) { return d.name + ": " + format(d.value); });

      node.append("circle")
        .attr("r", function(d) { return d.r; })
        .style("fill", function(d) { return color(d.status); });

      node.append("text")
        .attr("dy", ".3em")
        .style("text-anchor", "middle")
        .text(function(d) { return d.addr; });
    }

    connection.onopen = function (session) {

        var received = 0;

        function onevent1(args) {

            message = jQuery.parseJSON(args);
            logMessage(message);

            for (var key in message) {
                console.log("got key " + key);
                if (key === "FIXING") {
                    var target = "A" + message[key].replace(/\./g, "d");
                    console.log("got fixing *" + target + "*");
                    d3.select("#" + target).classed("success", false);
                    d3.select("#" + target).classed("warning", true);
                } else if (key === "FIXED") {
                    var target = "A" + message[key].replace(/\./g, "d");
                    d3.select("#" + target).classed("warning", false);
                    d3.select("#" + target).classed("success", true);
                } else if (key === "NEWNODE") {
                    setTimeout(function() {
                        d3.json("members", memberTable);}, 200);
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

    
    d3.select(self.frameElement).style("height", diameter + "px");

})();
