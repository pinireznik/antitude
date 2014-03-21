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

    function logMessage(message) {

        for (var key in message) {
            $("#message_log").append(key + " " + message[key] + "<br/>");
        }

    }
    function memberTable(error, json) {
        if (error) {
            return console.warn(error);
        }
        console.log("JSON: " + json);
        console.log("member0: " + json.members[0].name);

        var table = d3.select("#node_table").html("").append("table")
            .attr("class", "table table-bordered table-condensed");
        tbody = table.append("tbody");

        for (var i = 0; i < json.members.length; i++) {
            var m = json.members[i];
            var id = "A" + m.addr.split(":")[0].replace(/\./g, "d");
            console.log("id " + id);
            var tr = tbody.append("tr").attr("id", id);
            tr.append("td").text(m.name);
            tr.append("td").text(m.addr);
            tr.append("td").text(m.status);
        }

        var thead = table.append("thead");
        thead.append("th").text("Name");
        thead.append("th").text("Address");
        thead.append("th").text("Status");

        memberGraph(json);
    }

    function memberGraph(json) {

      console.log("In member graph");
      console.log(json.members);
      var node = svg.selectAll(".node")
        .data(bubble.nodes({children: json.members}))
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


    d3.json("members", memberTable);

    
    d3.select(self.frameElement).style("height", diameter + "px");

})();
