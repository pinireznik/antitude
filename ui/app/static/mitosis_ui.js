(function() {

    var connection = new autobahn.Connection({
        url: 'ws://127.0.0.1:5000/ws',
        realm: 'realm1'}
        );

    function logMessage(message) {

        for (var key in message) {
            $("#message_log").append(key + " " + message[key] + "<br/>");
        }

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


    d3.json("members", function(error, json) {
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


    });
})();
