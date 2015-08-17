var chat = (function() {
	var SCRIPT_ROOT = "";
	var handle = null;

	// Process Ajax Data
	function ajax_complete(data, status) {
		if (status == "success") {
			var obj = $.parseJSON(data.responseText);
			$(".view").html("");
			$.each(obj, function (index, value) {
				$(".view").append("<tr><td>" + value.username + "</td><td>" +
					value.message + "</td></tr>");
			});
		} else if (status != "notmodified") {
			console.log(status);
		}
	}

	function start_ajax(sid) {
		handle = setInterval(function(){
			$.ajax({
				complete: ajax_complete,
				method:   "GET",
				url:      SCRIPT_ROOT + "/api/token/" + sid +"/chat/"
			});
		}, 2000);
	}

	function stop_ajax(sid) {
		clearInterval(handle);
	}

	return {
		start: start_ajax,
		stop: stop_ajax
	}
})();
