(function() {

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

    var colors = { "alive": "green", "failed": "red"};
/*
    var svg = d3.select("#node_graph").append("svg")
      .attr("width", diameter)
      .attr("height", diameter)
      .attr("class", "bubble");
*/
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

          var id = "A" + m.addr.split(":")[0].replace(/\./g, "d");
          if (!(id in nodes)) {
            //Set a default value for memory
            nodes[id] = {"memory": 20};
          }
          nodes[id].addr = m.addr;
          nodes[id].name = m.name; //Yes, I know
          nodes[id].status = m.status;
          nodes[id].id = "A" + m.addr.split(":")[0].replace(/\./g, "d");
        }
        //Should also delete any nodes that don't appear in list

        updateMemberTable();
        updateGraph();
    }

    function updateMemberTable() {

        var table = d3.select("#node_table").html("").append("table")
            .attr("class", "table table-bordered table-condensed");
        tbody = table.append("tbody");

        for (var id in nodes) {
            var n = nodes[id];
            var tr = tbody.append("tr").attr("id", id);
            tr.append("td").text(n.name);
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
      for (var id in nodes) {
        children.push(nodes[id]);
      }
      return children;
    }

    function updateGraph() {


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
          return "translate(" + d.x + "," + d.y + ")"; });

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
    }

    function addrToId(addr) {
      return "A" + addr.replace(/\./g, "d");
    }

    function extractArg(arg, string) {

      var re = new RegExp(arg + "=(\\S*)");
      res = re.exec(string);
      if (res && res.length > 1) {
        return  re.exec(string)[1];
      }
      return "";
    }

    connection.onopen = function (session) {

        var received = 0;

        function onevent1(args) {

            message = jQuery.parseJSON(args);
            logMessage(message);

            for (var key in message) {
                console.log("got key " + key);
                if (key === "FIXING") {
                    var target = addrToId(message[key]);
                    console.log("got fixing *" + target + "*");
                    d3.select("#" + target).classed("success", false);
                    d3.select("#" + target).classed("warning", true);
                } else if (key === "FIXED") {
                    var target = "A" + message[key].replace(/\./g, "d");
                    d3.select("#" + target).classed("warning", false);
                    d3.select("#" + target).classed("success", true);
                } else if (key === "NEWNODE") {
                    setTimeout(function() {
                        d3.json("members", updateNodes);}, 200);
                } else if (key === "MEMORY_LEVEL") {
                  var level = extractArg("LEVEL", message[key]);
                  var target = extractArg("IP", message[key]);
                  console.log("LEVEL= " + level + " IP= " + target);

                  if (level !== "" && target !== "") {
                    console.log("updating level for " + addrToId(target));
                    nodes[addrToId(target)].memory = +level;
                    updateMemberTable();
                    updateGraph();
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

    
    d3.select(self.frameElement).style("height", diameter + "px");

})();
