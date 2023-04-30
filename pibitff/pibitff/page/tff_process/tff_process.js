frappe.pages['tff-process'].on_page_load = function(wrapper) {
	let title = "Transactional Process";
	let route = frappe.get_route();
	if (route.length > 0) {
		title = title + ": " + route[1];
	}
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: title,
		single_column: true
	});

	// hot reload in development
	if (frappe.boot.developer_mode) {
		frappe.hot_update = frappe.hot_update || [];
		frappe.hot_update.push(() => load_tff_process(wrapper));
	}
};

frappe.pages['tff-process'].on_page_show = function (wrapper) {
	load_tff_process(wrapper);
};

function load_tff_process(wrapper) {
	let route = frappe.get_route();
	if (route.length > 0) {
		let docname = route[1];

		let $parent = $(wrapper).find(".layout-main-section");
		$parent.empty();

		frappe.require("tff_process.bundle.js").then(() => {
			frappe.tff_process = new frappe.ui.TffProcess({
				wrapper: $parent,
				page: wrapper.page,
				docname: docname
			});
		});
	}

}