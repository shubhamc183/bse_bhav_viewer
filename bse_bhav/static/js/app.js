var dtTopStocks;
var dtSearchStocks;
$(document).ready(
		function() {
			dtTopStocks = $('#dtTopStocks').DataTable({
				searching : false,
				info : false,
				paging : false,
				aaSorting : [ [ 6, 'des' ] ],
			});
			dtSearchStocks = $('#dtSearchStocks').DataTable({
				searching : false,
				info : true,
				ordering : false,
			});
			$('.dataTables_length').addClass('bs-select');
			$.ajax({
				url : "get_top_stocks",
				success : function(data, status, xhr) {
					addStocksDataToDataTable(dtTopStocks, data);
				}
			});
			$('#stockSearchButton').click(
					function() {
						dtSearchStocks.clear().draw();
						$.ajax({
							url : "get_stocks_by_name?stock_name="
									+ $('#stockSearchInput').val(),
							success : function(data, status, xhr) {
								addStocksDataToDataTable(dtSearchStocks, data);
							}
						});
					});
			$("#reindexStocksData").click(function() {
				$.ajax({
					url : "save_latest_bhav_report",
					success : function(data, status, xhr) {
						var json = $.parseJSON(data);
						alert(json["msg"]);
						if (json["success"]) {
							location.reload();
						}
					}
				});
			});

		});

function addStocksDataToDataTable(table, data) {
	var json = $.parseJSON(data);
	if (json["success"]) {
		$.each(json["data"], function(i, item) {
			table.row.add([ item["name"], item["code"], item["open"],
					item["low"], item["high"], item["close"],
					item["percentage"] ]);
		});
		table.draw();
	} else {
		alert(json["msg"]);
	}
}